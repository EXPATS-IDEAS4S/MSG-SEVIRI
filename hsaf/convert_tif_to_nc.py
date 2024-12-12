import os
import glob
import rasterio
import xarray as xr
import pandas as pd
from rasterio.transform import Affine
from datetime import datetime
from glob import glob
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors

# Define the categories and their color mapping
CATEGORY_COLORS = {
    0: "white",      # Snow
    42: "gray",      # Cloud
    85: "green",     # Land
    170: "blue",     # Sea
    212: "black",    # Dark
    233: "lightgray",# No Data
    255: "purple"    # Space
}
CATEGORY_LABELS = {
    0: "Snow",
    42: "Cloud",
    85: "Land",
    170: "Sea",
    212: "Dark",
    233: "No Data",
    255: "Space"
}
def plot_dataset(dataset, output_folder, time_index=0, title="Categorical Data Plot"):
    """
    Plots a categorical xarray dataset on a geographic map using cartopy.

    Parameters:
    - dataset (xarray.Dataset): The dataset to plot, with dimensions 'lat' and 'lon'.
    - time_index (int): Index of the time step to plot (for datasets with a time dimension).
    - title (str): Title for the plot.

    Returns:
    - None
    """
    # Extract data for the specified time step
    plot_time = str(dataset.time.values).split('.')[0]
    # extract snow cover values
    data = dataset['value']
    
    # Set up the figure and the cartopy projection
    fig, ax = plt.subplots(
        figsize=(10, 6),
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    ax.set_title(f"{title} - Time: {plot_time}", fontsize=14)
    
    # Add features: coastlines, borders, gridlines
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    gl = ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

    gl.right_labels = False  # Disable longitude labels on the right
    gl.top_labels = False    # Disable latitude labels on the top

    # Set up a colormap and normalization based on category colors
    cmap = mcolors.ListedColormap([CATEGORY_COLORS[key] for key in CATEGORY_COLORS.keys()])
    bounds = list(CATEGORY_COLORS.keys()) + [256]  # Set upper bound for colors
    norm = mcolors.BoundaryNorm(bounds, cmap.N)

    # Plot the data
    img = ax.pcolormesh(
        dataset.lon, dataset.lat, data,
        transform=ccrs.PlateCarree(),
        cmap=cmap,
        norm=norm
    )
    
    # Create a custom legend with labels
    handles = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=cmap(norm(val)), markersize=10, label=label)
        for val, label in CATEGORY_LABELS.items()
    ]
    ax.legend(handles=handles, title="Categories", loc="lower left", bbox_to_anchor=(1, 0))

    fig.savefig(f'{output_folder}.png', bbox_inches="tight", dpi=300)
    plt.close()


year = '2014'

# Set the path to the folder containing your .tif files
tif_folder = f"/data/sat/msg/H_SAF/H10_WGS84/{year}/"
list_of_files = sorted(glob(tif_folder + '*.tif'))

output_nc_folder = f'/data/sat/msg/H_SAF/H10_nc/{year}/' 
output_fig_folder = '/data/sat/msg/H_SAF/H10_fig/'  
os.makedirs(output_nc_folder, exist_ok=True)

# Define target grid boundaries and step size
lat_min, lat_max, lon_min, lon_max = 42, 51.5, 5, 16
lat_step, lon_step = 0.04, 0.04

# Create target latitude and longitude arrays
target_lats = np.arange(lat_min, lat_max + lat_step, lat_step)
target_lons = np.arange(lon_min, lon_max + lon_step, lon_step)
#print(target_lats.shape)
#print(target_lons.shape)

# Define a function to extract date from filename (assuming it's encoded in the filename)
def extract_date_from_filename(filename):
    # Modify this function based on your filename structure
    # Example: if filename is like 'h10_20131001_day_merged.tif', extract date
    basename = os.path.basename(filename)
    date_str = basename.split('_')[1] # Example: '20230101'
    return datetime.strptime(date_str, "%Y%m%d")


def convert_and_regrid_tif_to_nc(filename, tif_folder, output_nc_folder, output_fig_folder):
    with rasterio.open(os.path.join(tif_folder, filename)) as src:
        # Check if CRS is WGS84 (EPSG:4326)
        if src.crs.to_string() != "EPSG:4326":
            print(f"File {filename} is not in WGS84 (EPSG:4326), skipping.")
            return
        
        # Read data and define original coordinates
        data = src.read(1)
        #print(data.shape)
        transform = src.transform
        height, width = data.shape
        orig_lons = np.linspace(transform[2], transform[2] + transform[0] * width, width)
        orig_lats = np.linspace(transform[5], transform[5] + transform[4] * height, height)[::-1]
        #print(orig_lats.shape)
        #print(orig_lons.shape)

        # Create initial Dataset
        date_str = filename.split("_")[1].replace(".tif", "")
        date = datetime.strptime(date_str, "%Y%m%d")
        da = xr.DataArray(np.flipud(data), dims=("lat", "lon"), coords={"lat": orig_lats, "lon": orig_lons, "time": date}, name="value")
        dataset = xr.Dataset({"value": da})
        #print(dataset)
        #exit()

        # Regrid to target grid using nearest-neighbor interpolation
        regridded_dataset = dataset.interp(lat=target_lats, lon=target_lons, method="nearest")
        #print(regridded_dataset)

        # Save regridded dataset to a NetCDF file
        output_nc_path = os.path.join(output_nc_folder, f"{filename.replace('.tif', '.nc')}")
        regridded_dataset.to_netcdf(output_nc_path)
        print(f"Saved regridded dataset to {output_nc_path}")
        plot_dataset(regridded_dataset, output_fig_folder+filename.split('.')[0], title="H10 Product")

# Process and regrid all .tif files in the folder
for filename in sorted(os.listdir(tif_folder)):
    if filename.endswith(".tif"):
        convert_and_regrid_tif_to_nc(filename, tif_folder, output_nc_folder, output_fig_folder)
        #exit()
