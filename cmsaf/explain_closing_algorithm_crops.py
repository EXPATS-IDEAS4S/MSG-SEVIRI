import os
from glob import glob
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import matplotlib.colors as mcolors
from scipy.ndimage import binary_dilation, binary_erosion, binary_closing

# Path to the folder containing NetCDF files
folder_path = "/data/sat/msg/CM_SAF/merged_cloud_properties/2013/04"
file_list = sorted(glob(os.path.join(folder_path, "*.nc")))
output_path = "/home/dcorradi/Documents/Fig/cma/"

# Define a custom colormap with meaningful colors
cmap = mcolors.ListedColormap(['black', 'white'])
norm = mcolors.BoundaryNorm(boundaries=[0, 1, 2], ncolors=2)

# Loop through each file
for file in file_list:
    print(f"Processing file: {file}")
    
    # Open the NetCDF file
    with xr.open_dataset(file) as ds:
        lat = ds['lat'].values
        lon = ds['lon'].values
        # Create grid
        lat_grid, lon_grid = np.meshgrid(lat, lon, indexing='ij')
        # Get the time values
        times = ds['time'].values

        for i, time in enumerate(times):
            print(time)
            cma = ds['cma'].values[i, :, :]

            # Apply morphological operations
            dilation = binary_dilation(cma, structure=np.ones((3, 3)))
            erosion = binary_erosion(cma, structure=np.ones((3, 3)))
            closing = binary_closing(cma, structure=np.ones((3, 3)))

            # Create the plot with 4 subplots
            fig, axes = plt.subplots(1, 4, figsize=(16, 6), subplot_kw={'projection': ccrs.PlateCarree()})

            titles = ["Original CMA", "Dilation", "Erosion", "Closing"]
            data_list = [cma, dilation, erosion, closing]

            for ax, data, title in zip(axes, data_list, titles):
                ax.coastlines(resolution='50m', color='red', linewidth=0.8, linestyle=':')
                ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.8, edgecolor='red')
                ax.add_feature(cfeature.LAND, linestyle=':', edgecolor='red', facecolor='lightgray')
                ax.add_feature(cfeature.OCEAN, facecolor='white')

                # Plot the data
                data_plot = ax.pcolormesh(lon, lat, data, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
                ax.set_title(title, fontsize=12, fontweight='bold')

            # Add a shared colorbar
            cbar = fig.colorbar(data_plot, ax=axes, orientation='vertical', shrink=0.6, pad=0.05)
            cbar.set_ticks([0.5, 1.5])
            cbar.set_ticklabels(['Clear', 'Cloudy'])

            # Add a title for the entire figure
            fig.suptitle(f"Cloud Mask Analysis: {str(time).split('.')[0]}", fontsize=16, fontweight='bold')

            # Save the plot
            plt.savefig(f"{output_path}cma_closing_analysis_{time}.png", dpi=300, bbox_inches='tight')
            plt.close()
            exit()
