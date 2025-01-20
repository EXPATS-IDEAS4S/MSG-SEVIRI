import os
import glob
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from glob import glob
import numpy as np
import matplotlib.colors as mcolors

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
        # Access the `cma` variable
        #cma = ds['cma'].values
        lat = ds['lat'].values
        lon = ds['lon'].values
        #create grid
        lat_grid, lon_grid = np.meshgrid(lat, lon, indexing='ij')
        # get the time values
        times = ds['time'].values

        for i,time in enumerate(times):
            print(time)
            cma = ds['cma'].values[i,:,:]
            #extract the values in ds for this time

            # Create the plot
            plt.figure(figsize=(6, 6))
            ax = plt.axes(projection=ccrs.PlateCarree())
            ax.coastlines(resolution='50m', color='red', linewidth=0.8, linestyle=':')
            ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.8, edgecolor='red')
            ax.add_feature(cfeature.LAND, linestyle=':', edgecolor='red', facecolor='lightgray')
            ax.add_feature(cfeature.OCEAN, facecolor='white')

            # Plot the data
            cma_plot = plt.pcolormesh(lon, lat, cma, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())

            # Add a colorbar with labels for each category
            cbar = plt.colorbar(cma_plot, ax=ax, orientation='vertical', shrink=0.6, pad=0.05)
            cbar.set_ticks([0.5, 1.5])
            cbar.set_ticklabels(['Clear', 'Cloudy'])
            
            # Add title and labels
            ax.set_title(f"{str(time).split('.')[0]}", fontsize=14, fontweight='bold')

            # Save the plot
            plt.savefig(f"{output_path}cma_{time}.png", dpi=300, bbox_inches='tight')
        exit()
            
        
