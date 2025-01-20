import os
from glob import glob
import pandas as pd
import numpy as np
import xarray as xr
from scipy.spatial import cKDTree
from datetime import datetime

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
hsaf_path = '/data/sat/msg/H_SAF/H10_nc/201*'
hsaf_filepattern = 'h10_201*_day_merged.nc'
cmsaf_path = '/data/sat/msg/CM_SAF/CMA_processed/*/*/*'
cmsaf_filepattern = 'CMAin*.nc'
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/filling_cma_figs/"

# # Placeholder for results
# output_data = []

# # Find all the HSAF snow files
# hsaf_files = sorted(glob(hsaf_path + '/' + hsaf_filepattern))

# # Process each HSAF file
# for hsaf_file in hsaf_files:
#     print(f"Processing HSAF snow file: {hsaf_file}")

#     # Extract date from HSAF file name (assuming it's embedded in the filename)
#     date_str = hsaf_file.split('/')[-1].split('_')[1]  # Format: '20130302'
#     print(date_str)
#     #date = datetime.strptime(date_str, '%Y%m%d')
#     #print(date)

#     # Open HSAF snow cover file
#     with xr.open_dataset(hsaf_file) as hsaf_ds:
#         snow_cover = hsaf_ds['value'].values
#         lat_snow = hsaf_ds['lat'].values
#         lon_snow = hsaf_ds['lon'].values

#     # Filter the snowy pixels (value 0 represents snow)
#     snowy_pixels = np.where(snow_cover == 0)
#     #print(snowy_pixels) # row and column indices of snowy pixels

#     # For snowy pixels, find the corresponding CMSAF files (there are many CMSAF files per day)
#     cmsaf_files = sorted(glob(cmsaf_path + f'/CMAin{date_str}*'))  # Get all CMSAF files for that day
   
#     for cmsaf_file in cmsaf_files:
#         print(f"Processing CMSAF cloud mask file: {cmsaf_file}")

#         # Open CMSAF cloud mask file
#         with xr.open_dataset(cmsaf_file) as cmsaf_ds:
#             cloud_mask = cmsaf_ds['cma'].values  
#             lat_cmsaf = cmsaf_ds['lat'].values
#             lon_cmsaf = cmsaf_ds['lon'].values
#             time_cmsaf = pd.to_datetime(cmsaf_ds['time'].values)[0] 

#         # Build a KDTree for efficient spatial matching between snowy pixels and CMSAF grid
#         lat_cmsaf, lon_cmsaf = np.meshgrid(lat_cmsaf, lon_cmsaf, indexing='ij')
#         cmsaf_coords = np.column_stack((lat_cmsaf.ravel(), lon_cmsaf.ravel()))
#         tree = cKDTree(cmsaf_coords)

#         # Iterate over snowy pixels and get the closest cloud mask values from CMSAF
#         for lat, lon in zip(lat_snow[snowy_pixels[0]], lon_snow[snowy_pixels[1]]):
#             # Find the nearest cloud mask pixel from the CMSAF grid
#             dist, idx = tree.query([lat, lon])
#             cloud_mask_value = cloud_mask.ravel()[idx]
           
#             output_data.append({
#                 'time': time_cmsaf,
#                 'lat': lat,
#                 'lon': lon,
#                 'cloud_mask': cloud_mask_value
#             })

# # Convert the output data into a DataFrame
# result_df = pd.DataFrame(output_data)

# # Save the result to a CSV file
# output_csv = f'{output_path}output_snow_and_cloud_mask.csv'
# result_df.to_csv(output_csv, index=False)

# print(f"Results saved to {output_csv}")

# Open the CSV file to verify the results
df = pd.read_csv( f'{output_path}output_snow_and_cloud_mask.csv')
print(df)
exit()

# Mapping of cloud mask values to categories
CLOUD_MASK_CATEGORIES = {
    0: "Clear",
    1: "Cloudy"
}

# Step 1: Add the cloud mask category to the dataframe
df['cloud_mask_category'] = df['cloud_mask'].map(CLOUD_MASK_CATEGORIES)

# Step 2: Normalize the counts by category
# Group by cloud mask category and count occurrences
counts = df['cloud_mask_category'].value_counts()

# Calculate normalized counts
normalized_counts = counts / counts.sum()

# Step 3: Create a new dataframe for normalized counts
normalized_df = pd.DataFrame({
    'cloud_mask_category': normalized_counts.index,
    'normalized_count': normalized_counts.values
})

# Display the result
print(normalized_df)

# plot the results
import matplotlib.pyplot as plt
import seaborn as sns

# Plot the normalized counts of each category
fig, axes = plt.subplots(figsize=(5, 3))
sns.barplot(data=normalized_df, x='cloud_mask_category', y='normalized_count', ax=axes)
plt.ylabel('Normalized Count', fontsize=12)
plt.xlabel('CMSAF Category', fontsize=12)
plt.yticks(fontsize=12)
plt.xticks(fontsize=12)
plt.title('Cloud Mask Categories of Snowy Pixels', fontsize=12, fontweight='bold')
plt.savefig(f'{output_path}cloud_mask_category_distribution_of_snowy_pixels.png', bbox_inches='tight')

