import xarray as xr
import numpy as np
import pandas as pd
import glob
from scipy.ndimage import binary_closing
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Define paths
cmsaf_folder = "/data1/crops/cmsaf_2013-2014-2015-2016_expats/nc_clouds/"
modis_folder = "/data1/other_data/MODIS/2013/"
cmsaf_files = sorted(glob.glob(f"{cmsaf_folder}2013*_EXPATS_0.nc"))
modis_files = sorted(glob.glob(f"{modis_folder}CLDMSK_L2_MODIS_Aqua*.nc"))
print(modis_files)
exit()

output_path = "/home/Daniele/fig/cma_analysis/modis/"

# Define spatial domain
lon_min, lon_max = 5, 16
lat_min, lat_max = 42, 51.5

# Initialize dataframe to store results
results = []

def apply_closing(mask, structure_size):
    """Applies the binary closing algorithm with a given kernel size."""
    structure = np.ones((structure_size, structure_size), dtype=bool)
    closed_mask = binary_closing(mask, structure=structure)
    holes = (closed_mask - mask) == 1  # Find holes in the mask
    return holes

def get_modis_matching_files(start_time, end_time):
    """Find MODIS files within the time range of CMSAF product."""
    matching_files = []
    for modis_file in modis_files:
        ds = xr.open_dataset(modis_file)
        modis_start = ds.attrs["time_coverage_start"]
        modis_end = ds.attrs["time_coverage_end"]
        print(start_time, end_time)
        print(modis_start, modis_end)
        if modis_start >= start_time and modis_end <= end_time:
            matching_files.append(modis_file)
            print(f"Found matching MODIS file: {modis_file}")
            exit()
    return matching_files

for cmsaf_file in cmsaf_files:
    # Open CMSAF dataset
    cmsaf_ds = xr.open_dataset(cmsaf_file)

    # Extract the time_coverage_start from the dataset
    cmsaf_time_start = cmsaf_ds.time.values

    # Convert to datetime and format as required in string
    cmsaf_time_start_dt = pd.to_datetime(cmsaf_time_start)  # Convert to Python datetime
    cmsaf_time_start_formatted = cmsaf_time_start_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Calculate the end time (start + 15 minutes)
    cmsaf_time_end_dt = cmsaf_time_start_dt + timedelta(minutes=15)
    cmsaf_time_end_formatted = cmsaf_time_end_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    # Extract cloud mask and spatial coords  (0 for clear sky, 1 for cloudy)
    mask = cmsaf_ds["cma"].values#.sel(lat=slice(lat_max, lat_min), lon=slice(lon_min, lon_max))
    lat_min = cmsaf_ds.lat.values.min()
    lat_max = cmsaf_ds.lat.values.max()
    lon_min = cmsaf_ds.lon.values.min()
    lon_max = cmsaf_ds.lon.values.max()

    # Apply 3x3 and 5x5 closing
    holes_3x3 = apply_closing(mask, 3)
    holes_5x5 = apply_closing(mask, 5)

    # Get coordinates of the holes
    lat_3x3, lon_3x3 = np.where(holes_3x3)
    lat_5x5, lon_5x5 = np.where(holes_5x5)
    # lat_array = cmsaf_ds.lat.values
    # lon_array = cmsaf_ds.lon.values
    # lat_grid, lon_grid = np.meshgrid(lat_array, lon_array, indexing="ij")

    # lat_3x3 = lat_grid[holes_3x3]
    # lon_3x3 = lon_grid[holes_3x3]
    # lat_5x5 = lat_grid[holes_5x5]
    # lon_5x5 = lon_grid[holes_5x5]  
   

    # Find matching MODIS files
    matching_modis_files = get_modis_matching_files(cmsaf_time_start_formatted, cmsaf_time_end_formatted)

    if not matching_modis_files:
        continue

    # Determine the MODIS file with the highest spatial coverage in the domain
    max_coverage = -1
    best_modis_file = None
    for modis_file in matching_modis_files:
        # Open the geolocation_data group of the MODIS file
        with xr.open_dataset(modis_file, group="geolocation_data") as modis_geo_ds:
            # Select the latitude and longitude subset within the defined domain
            lat_grid_modis = modis_geo_ds["latitude"].values
            lon_grid_modis = modis_geo_ds["longitude"].values
            
            lat_subset = (lat_grid_modis >= lat_min) & (lat_grid_modis <= lat_max)
            lon_subset = (lon_grid_modis >= lon_min) & (lon_grid_modis <= lon_max)
            print(lat_subset)
            print(lon_subset)
            exit()

            # Compute coverage: count valid pixels in the spatial subset
            valid_lat_lon_mask = lat_subset & lon_subset 
            coverage = np.sum(valid_lat_lon_mask.values)
            
            # Update the best MODIS file if this one has greater coverage
            if coverage > max_coverage:
                max_coverage = coverage
                best_modis_file = modis_file

    if best_modis_file:
        # Open the geophysical and geolocation data groups
        with xr.open_dataset(best_modis_file, group="geophysical_data") as cloud_mask_ds, \
            xr.open_dataset(best_modis_file, group="geolocation_data") as geo_ds:

            # Extract relevant data
            cloud_mask = cloud_mask_ds['Integer_Cloud_Mask'].values
            latitude = geo_ds['latitude'].values
            longitude = geo_ds['longitude'].values

            # Initialize an empty list to store results
            results = []

            # Define a helper function to match CMSAF holes with MODIS pixels
            def match_pixels(condition_label, cmsaf_lat, cmsaf_lon, cmask_np):
                for lat, lon in zip(cmsaf_lat, cmsaf_lon):
                    # Use the nearest neighbor approach to locate MODIS pixel
                    modis_pixel = cmask_np
                    results.append({"Condition": condition_label, "MODIS Value": modis_pixel})

            # Match CMSAF holes for both conditions
            match_pixels("3x3", lat_3x3, lon_3x3)
            match_pixels("5x5", lat_5x5, lon_5x5)

# Create a dataframe
results_df = pd.DataFrame(results)

# Replace MODIS values with labels
modis_labels = {0: "Cloudy", 1: "Probably Cloudy", 2: "Probably Clear", 3: "Confident Clear"}
results_df["MODIS Value"] = results_df["MODIS Value"].map(modis_labels)

# Plot distribution
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(data=results_df, x="MODIS Value", hue="Condition")
plt.title("Distribution of MODIS Cloud Mask Values in CMSAF Clear Holes", fontsize=16, fontweight="bold")
plt.xlabel("MODIS Cloud Mask Value", fontsize=14)
plt.ylabel("Count", fontsize=14)
plt.legend(title="Condition", fontsize=12)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
fig.savefig(f"{output_path}modis_cma_comparison.png", dpi=300, bbox_inches="tight")
