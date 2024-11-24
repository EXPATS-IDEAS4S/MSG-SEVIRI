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
def plot_dataset(dataset, time_index=0, title="Categorical Data Plot"):
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
    if 'time' in dataset.dims:
        data = dataset.isel(time=time_index)['value']
        plot_time = str(dataset.time[time_index].values)
    else:
        data = dataset['value']
        plot_time = "No time dimension"
    
    # Set up the figure and the cartopy projection
    fig, ax = plt.subplots(
        figsize=(10, 6),
        subplot_kw={"projection": ccrs.PlateCarree()}
    )
    ax.set_title(f"{title} - Time: {plot_time}", fontsize=14)
    
    # Add features: coastlines, borders, gridlines
    ax.coastlines()
    ax.add_feature(cfeature.BORDERS, linestyle=":")
    ax.gridlines(draw_labels=True, dms=True, x_inline=False, y_inline=False)

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

    plt.show()


# Set the path to the folder containing your .tif files
tif_folder = "/data/sat/msg/H_SAF/H10_WGS84/2013/"
list_of_files = sorted(glob(tif_folder + '*.tif'))

output_nc_folder = '/data/sat/msg/H_SAF/H10_nc/2013/'  
os.makedirs(output_nc_folder, exist_ok=True)

# Define target grid boundaries and step size
lat_min, lat_max, lon_min, lon_max = 42, 51.5, 5, 16
lat_step, lon_step = 0.04, 0.04

# Create target latitude and longitude arrays
target_lats = np.arange(lat_min, lat_max + lat_step, lat_step)
target_lons = np.arange(lon_min, lon_max + lon_step, lon_step)
print(target_lats.shape)
print(target_lons.shape)

# Define a function to extract date from filename (assuming it's encoded in the filename)
def extract_date_from_filename(filename):
    # Modify this function based on your filename structure
    # Example: if filename is like 'h10_20131001_day_merged.tif', extract date
    basename = os.path.basename(filename)
    date_str = basename.split('_')[1] # Example: '20230101'
    return datetime.strptime(date_str, "%Y%m%d")


def convert_and_regrid_tif_to_nc(filename, tif_folder, output_nc_folder):
    with rasterio.open(os.path.join(tif_folder, filename)) as src:
        # Check if CRS is WGS84 (EPSG:4326)
        if src.crs.to_string() != "EPSG:4326":
            print(f"File {filename} is not in WGS84 (EPSG:4326), skipping.")
            return
        
        # Read data and define original coordinates
        data = src.read(1)
        print(data.shape)
        transform = src.transform
        height, width = data.shape
        orig_lons = np.linspace(transform[2], transform[2] + transform[0] * width, width)
        orig_lats = np.linspace(transform[5], transform[5] + transform[4] * height, height)[::-1]
        print(orig_lats.shape)
        print(orig_lons.shape)

        # Create initial Dataset
        date_str = filename.split("_")[1].replace(".tif", "")
        date = datetime.strptime(date_str, "%Y%m%d")
        da = xr.DataArray(data, dims=("y", "x"), coords={"lat": orig_lats, "lon": orig_lons, "time": date}, name="value")
        dataset = xr.Dataset({"value": da})

        # Regrid to target grid using nearest-neighbor interpolation
        regridded_dataset = dataset.interp(lat=target_lats, lon=target_lons, method="nearest")

        # Save regridded dataset to a NetCDF file
        output_nc_path = os.path.join(output_nc_folder, f"{filename.replace('.tif', '.nc')}")
        regridded_dataset.to_netcdf(output_nc_path)
        print(f"Saved regridded dataset to {output_nc_path}")
        plot_dataset(regridded_dataset, title="H10 Dataset Plot")

# Process and regrid all .tif files in the folder
for filename in sorted(os.listdir(tif_folder)):
    if filename.endswith(".tif"):
        convert_and_regrid_tif_to_nc(filename, tif_folder, output_nc_folder)
        exit()

'''
# Loop through all .tif files in the folder
for tif_file in list_of_files:
    print(f"Processing {tif_file}")

    # Get the date for the time dimension
    date = extract_date_from_filename(tif_file)
    print(date)

    # Open the .tif file with rasterio
    with rasterio.open(tif_file) as src:
        # Read the data as a 2D numpy array
        data = src.read(1)
        #print(src.crs)EPSG:4326
        exit()
            
        # Get the latitude and longitude coordinates from the raster metadata
        transform = src.transform
        height, width = data.shape
        
        # Create row and column indices
        rows, cols = np.meshgrid(np.arange(height), np.arange(width), indexing="ij")
        
        # Use rasterio's transform to get lat/lon for each pixel
        lons, lats = rasterio.transform.xy(transform, rows, cols, offset="center")
        lats = np.array(lats).reshape(data.shape)  # Ensure lat/lon are 2D arrays
        lons = np.array(lons).reshape(data.shape)

        # Create the Dataset with coordinates lat, lon, and time
        da = xr.DataArray(
            data,
            dims=("y", "x"),  # Use "y" and "x" as dimension names
            coords={
                "lat": (("y", "x"), lats),
                "lon": (("y", "x"), lons),
                "time": date
            },
            name="category"
        )
        dataset = xr.Dataset({"value": da})
        print(dataset)
        plot_dataset(dataset, title="H10 Dataset Plot")
        exit()

        filename = os.path.basename(tif_file)
        output_nc_path = os.path.join(output_nc_folder, f"{filename.replace('.tif', '.nc')}")
        dataset.to_netcdf(output_nc_path)
        print(f"Saved {output_nc_path}")
'''