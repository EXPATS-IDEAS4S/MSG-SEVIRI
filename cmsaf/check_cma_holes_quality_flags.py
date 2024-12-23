import os
from glob import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from datetime import datetime
from scipy.ndimage import binary_closing
from process_cma_functions import extract_data
from flags_category_names import cma_mapping, quality_mapping, conditions_mapping, status_flag_mapping

# Define paths
cma_crops_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/"
cma_product_path = "/data/sat/msg/CM_SAF/CMA_processed/"
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"

# Initialize datataframe to store the data
#dataframe = pd.DataFrame(columns=['time', 'lat', 'lon', 'quality', 'conditions', 'status_flag', 'structure'])
rows = []

# Get all NetCDF files from cma_crops_path
nc_files = sorted(glob(os.path.join(cma_crops_path, "2013*.nc")))

# Loop through files and accumulate data
for nc_file in nc_files:
    cma_ds = extract_data(nc_file, cma_product_path)
    if cma_ds:
        # Extract time from the file (assuming the time is in the file metadata or variable)
        file_time = cma_ds.time.values[0]
        print(file_time)
        # Get the cloud mask values
        cloud_mask = cma_ds.cma.values[0]
        latitudes = cma_ds.lat.values
        longitudes = cma_ds.lon.values
        #print(latitudes)
        #print(longitudes)
        # Create lat lon grid
        #lat_grid, lon_grid = np.meshgrid(latitudes, longitudes, indexing='ij')
        #print(lat_grid,lon_grid)

        # Apply closing operation on the cloud mask
        closed_masks = {
            '3x3': binary_closing(cloud_mask == 1, structure=np.ones((3, 3))),
            '5x5': binary_closing(cloud_mask == 1, structure=np.ones((5, 5)))
        }

        # Loop through each closed mask structure
        for structure, closed_mask in closed_masks.items():
            # Identify patches by taking the difference between the original and closed mask
            granular_mask = (closed_mask - cloud_mask) == 1
            #print(granular_mask)

            # Get indices where granular_mask is True
            indices = np.argwhere(granular_mask)
            #print(indices.shape) # each row represents a point in the 3x3 mask (ROW, COL)

            for idx in indices:
                lat, lon = latitudes[idx[0]], longitudes[idx[1]]
                quality_flag = cma_ds.quality.values[0][idx[0], idx[1]]
                conditions_flag = cma_ds.conditions.values[0][idx[0], idx[1]]
                status_flag = cma_ds.status_flag.values[0][idx[0], idx[1]]

                # Append to the dataframe
                rows.append({
                    'time': file_time,
                    'lat': lat,
                    'lon': lon,
                    'quality': quality_flag,
                    'conditions': conditions_flag,
                    'status_flag': status_flag,
                    'structure': structure
                })

dataframe = pd.DataFrame(rows)
print(dataframe)
# Save the dataframe to a CSV file
dataframe.to_csv(f'{output_path}cloud_mask_closed_points_flags.csv', index=False)
print("Data saved to CSV file.")


#566527 nohup






# # Plot distribution of flags for the closed points (3x3 mask)
# def plot_flag_distribution(flag_data, title, output_filename):
#     """Plot the distribution of flag values."""
#     flag_series = pd.Series(flag_data).map(quality_mapping).dropna()  # Adjust mapping for other flags
#     flag_counts = flag_series.value_counts(normalize=True)
#     fig, ax = plt.subplots(figsize=(8, 6))
#     sns.barplot(x=flag_counts.index, y=flag_counts.values, ax=ax)
#     ax.set_title(title)
#     ax.set_xlabel("Categories")
#     ax.set_ylabel("Normalized Counts")
#     ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")
#     plt.tight_layout()
#     plt.savefig(output_filename, bbox_inches='tight')
#     plt.close()

# # Plot distributions for 3x3 and 5x5 closing results
# plot_flag_distribution(quality_3x3, "Quality Flags for 3x3 Closed Points", f'{output_path}quality_flags_3x3.png')
# plot_flag_distribution(status_flag_3x3, "Status Flags for 3x3 Closed Points", f'{output_path}status_flags_3x3.png')
# plot_flag_distribution(conditions_3x3, "Conditions Flags for 3x3 Closed Points", f'{output_path}conditions_flags_3x3.png')

# plot_flag_distribution(quality_5x5, "Quality Flags for 5x5 Closed Points", f'{output_path}quality_flags_5x5.png')
# plot_flag_distribution(status_flag_5x5, "Status Flags for 5x5 Closed Points", f'{output_path}status_flags_5x5.png')
# plot_flag_distribution(conditions_5x5, "Conditions Flags for 5x5 Closed Points", f'{output_path}conditions_flags_5x5.png')
