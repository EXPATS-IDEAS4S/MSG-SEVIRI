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

output_path = "/home/Daniele/fig/cma_analysis/modis/"



# # Define spatial domain
# #lon_min, lon_max = 5, 16
# #lat_min, lat_max = 42, 51.5

# # Initialize dataframe to store results
# results = []

# def apply_closing(mask, structure_size):
#     """Applies the binary closing algorithm with a given kernel size."""
#     structure = np.ones((structure_size, structure_size), dtype=bool)
#     closed_mask = binary_closing(mask, structure=structure)
#     holes = (closed_mask - mask) == 1  # Find holes in the mask
#     return holes

# # Iterate over MODIS files first
# for modis_file in modis_files:
#     with xr.open_dataset(modis_file) as modis_ds:
#         modis_start_time = pd.to_datetime(modis_ds.attrs["time_coverage_start"]).tz_localize(None)
#         modis_end_time = pd.to_datetime(modis_ds.attrs["time_coverage_end"]).tz_localize(None)
#         print('MODIS scan times: ',modis_start_time, modis_end_time)

#     # Extract year, month, day, and hour-minute from MODIS time
#     modis_year = modis_start_time.year
#     modis_month = modis_start_time.month
#     modis_day = modis_start_time.day
#     modis_hour_min = modis_start_time.strftime("%H:%M")
#     #print(modis_year, modis_month, modis_day, modis_hour_min)

#     # Find the closest CMSAF file based on MODIS time
#     cmsaf_match = None
#     for cmsaf_file in cmsaf_files:
#         cmsaf_time_info = cmsaf_file.split("/")[-1].split("_")[1]  # Extract 'hh:MM'
#         cmsaf_start_time = datetime.strptime(f"{modis_year}{modis_month:02}{modis_day:02}T{cmsaf_time_info}", 
#                                              "%Y%m%dT%H:%M")
#         cmsaf_end_time = cmsaf_start_time + timedelta(minutes=15)
#         print('CMSAF scan times: ',cmsaf_start_time, cmsaf_end_time)

#         # Check if MODIS scan fits within CMSAF scan times
#         if cmsaf_start_time <= modis_start_time and modis_end_time <= cmsaf_end_time:
#             cmsaf_match = cmsaf_file
#             break

#     if not cmsaf_match:
#         # If no matching CMSAF file found, continue with the next MODIS file
#         continue

#     # Process the matched CMSAF file
#     print(f"Processing CMSAF file: {cmsaf_match}")
#     cmsaf_ds = xr.open_dataset(cmsaf_match)

#     # Extract cloud mask and spatial coords (0 for clear sky, 1 for cloudy)
#     mask = cmsaf_ds["cma"].values
#     cmsaf_lat = cmsaf_ds["lat"].values
#     cmsaf_lon = cmsaf_ds["lon"].values
#     lat_grid, lon_grid = np.meshgrid(cmsaf_lat, cmsaf_lon, indexing="ij")
#     # Find lat and lon bounds
#     lat_min, lat_max = cmsaf_lat.min(), cmsaf_lat.max()
#     lon_min, lon_max = cmsaf_lon.min(), cmsaf_lon.max()

#     # Apply 3x3 and 5x5 closing
#     holes_3x3 = apply_closing(mask, 3)
#     holes_5x5 = apply_closing(mask, 5)

#     # Get coordinates of the holes
#     lat_3x3, lon_3x3 = np.where(holes_3x3)
#     lat_5x5, lon_5x5 = np.where(holes_5x5)
#     #print(lat_3x3, lon_3x3)

#     # Determine the MODIS file with the highest spatial coverage in the domain
#     max_coverage = -1
#     best_modis_file = None

#     # Open geolocation data from MODIS file
#     with xr.open_dataset(modis_file, group="geolocation_data") as geo_ds:
#         latitude = geo_ds["latitude"].values
#         longitude = geo_ds["longitude"].values

#         # Subset within the defined domain
#         lat_mask = (latitude >= lat_min) & (latitude <= lat_max)
#         lon_mask = (longitude >= lon_min) & (longitude <= lon_max)
#         spatial_coverage = np.sum(lat_mask & lon_mask)

#         if spatial_coverage > max_coverage:
#             max_coverage = spatial_coverage
#             best_modis_file = modis_file

#     if not best_modis_file:
#         continue

#     # Open geophysical data from the best MODIS file
#     with xr.open_dataset(best_modis_file, group="geophysical_data") as cloud_mask_ds:
#         print(f"Processing MODIS file: {best_modis_file}")
#         cloud_mask = cloud_mask_ds['Integer_Cloud_Mask'].values

#         # Map CMSAF holes to MODIS pixels
#         def map_holes_to_modis(lat_indices, lon_indices, condition_label):
#             # Loop over each hole (lat, lon) in the CMSAF grid
#             for lat_idx, lon_idx in zip(lat_indices, lon_indices):
#                 # Find the nearest MODIS pixel by finding the minimum absolute distance in both lat and lon
#                 lat_point = lat_grid[lat_idx, lon_idx]
#                 lon_point = lon_grid[lat_idx, lon_idx]
#                 #print(lat_point, lon_point)
#                 # Compute the squared distance for all points in the grid
#                 distance = (latitude - lat_point) ** 2 + (longitude - lon_point) ** 2

#                 #Find the minimum distance (square root of the sum of the squares)
#                 min_distance = np.min(np.sqrt(distance))
#                 #print(min_distance)
            
#                 if min_distance<0.04:
#                     # Find the index of the minimum distance
#                     min_index = np.unravel_index(np.argmin(distance), distance.shape)

#                     # Output the index and corresponding grid point
#                     closest_lat = latitude[min_index]
#                     closest_lon = longitude[min_index]
#                     cloud_mask_value = cloud_mask[min_index] 
#                 else:
#                     #print('No MODIS pixel found')
#                     continue   

#                 # Append the result including the condition, MODIS value, lat, lon, and scan times
#                 results.append({
#                     "Condition": condition_label,
#                     "MODIS Value": cloud_mask_value,
#                     "MODIS Lat": closest_lat,
#                     "MODIS Lon": closest_lon,
#                     "CMSAF Lat": lat_point,
#                     "CMSAF Lon": lon_point,
#                     "CMSAF Start Time": cmsaf_start_time,
#                     "CMSAF End Time": cmsaf_end_time,
#                     "MODIS Start Time": modis_start_time,
#                     "MODIS End Time": modis_end_time
#                 })

#         # Match pixels for 3x3 and 5x5
#         map_holes_to_modis(lat_3x3, lon_3x3, "3x3")
#         map_holes_to_modis(lat_5x5, lon_5x5, "5x5")

# # Create a dataframe
# results_df = pd.DataFrame(results)
# print(results_df)
# #save dataframe to csv
# results_df.to_csv(f"{output_path}modis_cma_comparison.csv")	

# Upload the csv file
results_df = pd.read_csv(f"{output_path}modis_cma_comparison.csv")

# Replace MODIS values with labels
modis_labels = {0: "Cloudy", 1: "Probably Cloudy", 2: "Probably Clear", 3: "Confident Clear"}
results_df["MODIS Value"] = results_df["MODIS Value"].map(modis_labels)

# Plot distribution
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(data=results_df, x="MODIS Value", hue="Condition")
plt.title("MODIS Cloud Mask Values in CMSAF Clear Holes", fontsize=16, fontweight="bold")
plt.xlabel("MODIS Cloud Mask Value", fontsize=14)
plt.ylabel("Count", fontsize=14)
plt.legend(title="Condition", fontsize=12)
# Place the ticks in order
plt.xticks(ticks=np.arange(4), labels=list(modis_labels.values()), fontsize=14)
plt.yticks(fontsize=14)
fig.savefig(f"{output_path}modis_cma_comparison.png", dpi=300, bbox_inches="tight")

#nohup 2000247