import os
from glob import glob
import pandas as pd
import numpy as np
import xarray as xr
from scipy.spatial import cKDTree

CATEGORY_LABELS = {
    0: "Snow",
    42: "Cloud",
    85: "Land",
    170: "Sea",
    212: "Dark",
    233: "No Data",
    255: "Space"
}

# Paths
snow_path = '/data/sat/msg/H_SAF/H10_nc/201*'
snow_filepattern = 'h10_201*_day_merged.nc'
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"
closed_pixels_df = pd.read_csv(f'{output_path}cloud_mask_closed_points_flags.csv')

# # Parse time column as datetime
# closed_pixels_df['time'] = pd.to_datetime(closed_pixels_df['time'])

# # Get unique dates from the closed_pixels_df
# unique_dates = closed_pixels_df['time'].dt.date.unique()

# # Find corresponding snow cover files
# snow_files = sorted(glob(snow_path + '/' + snow_filepattern))

# # Step 1: Identify unique structures
# unique_structures = closed_pixels_df['structure'].unique()
# print(f"Unique structures: {unique_structures}")

# # Placeholder for results
# results = []

# # Step 2: Process each structure separately
# for structure in unique_structures:
#     print(f"Processing structure: {structure}")

#     # Filter rows for the current structure
#     structure_df = closed_pixels_df[closed_pixels_df['structure'] == structure].copy()

#     # Create a lat-lon composite key
#     #structure_df['lat_lon'] = list(zip(structure_df['lat'], structure_df['lon']))

#     # Process snow files by matching dates
#     for date in unique_dates:
#         matching_snow_file = next(
#             (f for f in snow_files if date.strftime('%Y%m%d') in f), None
#         )
#         if not matching_snow_file:
#             print(f"No matching snow file found for {date}")
#             continue

#         print(f"Processing snow file: {matching_snow_file} for date: {date}")

#         # Open the matching snow cover file
#         with xr.open_dataset(matching_snow_file) as snow_ds:
#             snow_cover = snow_ds['value'].values
#             lat_snow = snow_ds['lat'].values
#             lon_snow = snow_ds['lon'].values

#         # Build KDTree for efficient spatial matching
#         lat_snow, lon_snow = np.meshgrid(lat_snow, lon_snow, indexing='ij')
#         snow_coords = np.column_stack((lat_snow.ravel(), lon_snow.ravel()))
#         tree = cKDTree(snow_coords)

#         # Filter rows for the current date
#         day_pixels = structure_df[structure_df['time'].dt.date == date]

#         # Match closed pixels to snow cover pixels
#         cma_coords = np.column_stack((day_pixels['lat'], day_pixels['lon']))
#         dist, idx = tree.query(cma_coords)
#         matched_snow_cover = snow_cover.ravel()[idx]

#         # Map snow cover values to categories
#         snow_cover_category = [CATEGORY_LABELS.get(value, "Unknown") for value in matched_snow_cover]

#         # Append data for the current date
#         day_pixels['snow_cover'] = snow_cover_category
#         results.append(day_pixels)

# # Step 3: Combine results
# final_df = pd.concat(results, ignore_index=True)

# # Save the new DataFrame to a CSV file
# output_csv = f'{output_path}output_snow_cover_by_structure.csv'
# final_df.to_csv(output_csv, index=False)
# print(f"Results saved to {output_csv}")


#plot the distribution of snow cover categories
import matplotlib.pyplot as plt
import seaborn

#open the saved csv file
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/filling_cma_figs/"
final_df = pd.read_csv(output_path + 'output_snow_cover_by_structure.csv')
#print(final_df)

# Normalize counts
normalized_df = (
    final_df
    .groupby(['snow_cover', 'structure'])
    .size()
    .reset_index(name='count')
)
normalized_df['normalized_count'] = (
    normalized_df['count'] / normalized_df.groupby('structure')['count'].transform('sum')
)

# Select normalized_df onl with structure 3x3
normalized_df = normalized_df[normalized_df['structure'] == '3x3']

#Change the structure column to True
normalized_df['structure'] = 'Yes'
print(normalized_df)


# Open hsaf dataset
folder_path = "/data/sat/msg/H_SAF/H10_nc/2013/"

#get list of filename
hsaf_files = sorted(glob(folder_path+'*/*.nc'))
print(len(hsaf_files))

#open dataset usinf xarray
# Open and merge files along the time dimension
merged_data = xr.open_mfdataset(
        hsaf_files, 
        combine='nested', 
        concat_dim='time', 
        parallel=True     
    )
print(merged_data)

# Access the 'value' data array
values = merged_data['value']

# Initialize a dictionary to store counts and norm counts for each category
category_counts = {label: 0 for label in CATEGORY_LABELS.values()}
print(category_counts)

# Compute the counts for each category
total_points = values.size
print(total_points)
for code, label in CATEGORY_LABELS.items():
    # Count occurrences and compute it
    count = (values == code).sum().compute().item()  # Count occurrences of the category
    category_counts[label] = count   # Normalize by total points
    #category_norm_counts[label] = count / total_points  # Normalize by total points

# Create a DataFrame from the results
df = pd.DataFrame.from_dict(category_counts, orient='index', columns=['count'])
df.reset_index(inplace=True)
df.rename(columns={'index': 'snow_cover'}, inplace=True)
df['normalized_count'] = df['count'] / total_points

# Delete rows with 0 counts
df = df[df['count'] > 0]

# Add a column called 'structure' to the final_df with all values as False
df['structure'] = 'No'

# Display the resulting DataFrame
print(df)

#Concate the two dataframes
final_df = pd.concat([normalized_df, df], ignore_index=True)
#change the column name 'structure' to 'closing_algorithm'
final_df.rename(columns={'structure': 'closed_pixels'}, inplace=True)
print(final_df)

# Plot the distribution of snow cover categories
fig, ax = plt.subplots(figsize=(6, 3))
seaborn.barplot(data=final_df, x='snow_cover',y='normalized_count', hue='closed_pixels', ax=ax)
plt.xlabel("HSAF Category", fontsize=12)
plt.ylabel("Normalized Count", fontsize=12)
plt.xticks(rotation=45, ha='right', fontsize=12)
plt.yticks(fontsize=12)
plt.legend(title='Closed Pixels', fontsize=12)
plt.title("HSAF category for the closed pixels", fontsize=12, fontweight='bold')
fig.savefig(f'{output_path}snow_cover_category_distribution.png', bbox_inches='tight')


















'''	
# Output DataFrame
output_data = []

# Define structure for the closing operation
structure_size = 5

# Get CMA and Snow Cover file lists
cma_files = sorted(glob.glob(os.path.join(cma_path, cma_filepattern)))
snow_files = sorted(glob.glob(os.path.join(snow_path, snow_filepattern)))

# Loop through CMA files
for cma_file in cma_files:
    print(f"Processing CMA file: {cma_file}")

    # Open CMA file
    with xr.open_dataset(cma_file) as cma_ds:
        cloud_mask = cma_ds['cma'].values  
        lat_cma = cma_ds['lat'].values
        lon_cma = cma_ds['lon'].values
        time_cma = pd.to_datetime(cma_ds['time'].values)  

    # Apply binary closing
    closed_mask = binary_closing(cloud_mask, structure=np.ones((structure_size, structure_size)))

    # Find closed pixels
    closed_indices = np.argwhere(closed_mask)
    if closed_indices.size == 0:
        continue

    # Get corresponding lat/lon of closed pixels
    closed_lats = lat_cma[closed_indices[:, 0], closed_indices[:, 1]]
    closed_lons = lon_cma[closed_indices[:, 0], closed_indices[:, 1]]

    # Find corresponding snow cover file
    snow_date = time_cma.strftime('%Y%m%d')
    matching_snow_file = next(
        (f for f in snow_files if f"snow_{snow_date}" in f), None
    )
    if not matching_snow_file:
        print(f"No matching snow cover file found for {time_cma}")
        continue

    # Open Snow Cover file
    with xr.open_dataset(matching_snow_file) as snow_ds:
        snow_cover = snow_ds['snow_cover'].values  # Replace with actual variable name
        lat_snow = snow_ds['latitude'].values
        lon_snow = snow_ds['longitude'].values

    # Build KDTree for efficient lat/lon matching
    snow_coords = np.column_stack((lat_snow.ravel(), lon_snow.ravel()))
    tree = cKDTree(snow_coords)

    # Match closed pixels to snow cover pixels
    cma_coords = np.column_stack((closed_lats, closed_lons))
    dist, idx = tree.query(cma_coords)
    matched_snow_cover = snow_cover.ravel()[idx]

    # Append data to output
    for i, (lat, lon, snow) in enumerate(zip(closed_lats, closed_lons, matched_snow_cover)):
        output_data.append({
            'datetime': time_cma,
            'lat': lat,
            'lon': lon,
            'snow_cover': snow
        })

# Create DataFrame
df = pd.DataFrame(output_data)

# Save DataFrame to a CSV file
output_csv = '/path/to/output_closed_pixels.csv'
df.to_csv(output_csv, index=False)
print(f"Results saved to {output_csv}")
'''