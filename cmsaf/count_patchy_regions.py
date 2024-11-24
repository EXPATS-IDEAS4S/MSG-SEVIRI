import xarray as xr
import numpy as np
from scipy.ndimage import binary_closing
from glob import glob
import os
from collections import defaultdict
import pandas as pd

from process_cma_functions import plot_cloud_mask, count_granular_points_by_orography, plot_normalized_histogram, plot_monthly_granular_distribution
from process_cma_functions import plot_normalized_histogram_from_csv, plot_monthly_granular_distribution_from_csv

# Define the path to the cloud mask files
folder_path_1 = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/'
folder_path_2 = '/work/dcorradi/crops/IR_108-WV_062-IR_039_2015-2016_128x128_EXPATS/nc_clouds/'
# List all the files in the folder
cma_filelist_1 = sorted(glob(folder_path_1 + '*.nc'))
cma_filelist_2 = sorted(glob(folder_path_2 + '*.nc'))

cma_filelist = cma_filelist_1 + cma_filelist_2

# Define the output folder for the figures
output_folder = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/filling_cma_figs/'

# Define the folder path for the orography data
orography_path = '/data/sat/msg/orography/'

#Open the orography data
orography_ds = xr.open_dataset(orography_path + 'DEM_EXPATS_0.01x0.01.nc')
print(orography_ds)

# Initialize dictionary to store cumulative counts
aggregated_counts = {'3x3': {'flat': 0, 'hills': 0, 'mountains': 0},
                     '5x5': {'flat': 0, 'hills': 0, 'mountains': 0}}

# Initialize dictionary to store the total number of points in each elevation category
total_points_by_category = {'flat': 0, 'hills': 0, 'mountains': 0}

# Initialize cumulative counts by month
monthly_counts = {
    '3x3': defaultdict(int),
    '5x5': defaultdict(int)
}

# Initialize cumulative counts by month
hourly_counts = {
    '3x3': defaultdict(int),
    '5x5': defaultdict(int)
}

# Initialize cumulative counts by month
monthly_counts_cloudy = {
    '3x3': defaultdict(int),
    '5x5': defaultdict(int)
}

# Initialize cumulative counts by month
hourly_counts_cloudy = {
    '3x3': defaultdict(int),
    '5x5': defaultdict(int)
}

for filename in cma_filelist:
    print(f"Processing {filename}")
    # Load the data
    data = xr.open_dataset(filename)
    cloud_mask = data['cma'].values  # Assuming 'cma' is the variable for cloud mask

    count_cloudy = np.sum(cloud_mask)

    lat = data['lat'].values
    lon = data['lon'].values

    # Apply binary closing with two different structures
    closed_mask_3x3 = binary_closing(cloud_mask, structure=np.ones((3, 3)))
    closed_mask_5x5 = binary_closing(cloud_mask, structure=np.ones((5, 5)))

    # Identify patches by taking the difference between the original and closed mask
    granular_mask_3x3 = (closed_mask_3x3 - cloud_mask) == 1  # Where 1 represents patchy clear in cloudy areas
    granular_mask_5x5 = (closed_mask_5x5 - cloud_mask) == 1

    num_features_3x3 = np.sum(granular_mask_3x3)
    num_features_5x5 = np.sum(granular_mask_5x5)  

    # Extract date from filename
    date = ' '.join(os.path.basename(filename).split('/')[-1].split('_')[0:2])
    #print(date)

    #get the month and hour from the date
    month = date[4:6]

    #Extract the date from the date
    hour = date.split(' ')[1].split(':')[0]
    #print(hour)    

    #plot_cloud_mask(cloud_mask, closed_mask_3x3, closed_mask_5x5, granular_mask_3x3, granular_mask_5x5, num_features_3x3, num_features_5x5, date, lat, lon, output_folder)  

    count, total_category_points = count_granular_points_by_orography(granular_mask_3x3, granular_mask_5x5, lat, lon, orography_ds)
    #print(count)

    # Update cumulative counts
    for mask_type in ['3x3', '5x5']:
        for category in ['flat', 'hills', 'mountains']:
            aggregated_counts[mask_type][category] += count[mask_type][category]

    # Update total points by elevation category
    for category in ['flat', 'hills', 'mountains']:
        total_points_by_category[category] += total_category_points[category]

    # Sum up the counts to get total granular points per month for each filter
    total_3x3 = sum(count['3x3'].values())
    total_5x5 = sum(count['5x5'].values())
    
    # Accumulate counts by month
    monthly_counts['3x3'][month] += total_3x3
    monthly_counts['5x5'][month] += total_5x5

    # Accumulate counts by hour
    hourly_counts['3x3'][hour] += total_3x3
    hourly_counts['5x5'][hour] += total_5x5

    # Accumulate counts by month for cloudy areas
    monthly_counts_cloudy['3x3'][month] += count_cloudy
    monthly_counts_cloudy['5x5'][month] += count_cloudy 

    # Accumulate counts by hour for cloudy areas
    hourly_counts_cloudy['3x3'][hour] += count_cloudy
    hourly_counts_cloudy['5x5'][hour] += count_cloudy

print(aggregated_counts)
print(total_points_by_category)
print(monthly_counts)
print(hourly_counts)
print(monthly_counts_cloudy)
print(hourly_counts_cloudy)

# Convert hourly_counts to DataFrame, transpose for readability, and save as CSV
df_hourly_counts_cloudy = pd.DataFrame(hourly_counts_cloudy).T
df_hourly_counts_cloudy.index.name = 'Hour'
df_hourly_counts_cloudy.reset_index().to_csv(f'{output_folder}hourly_counts_cloudy.csv', index=False)

# Convert monthly_counts to DataFrame, transpose for readability, and save as CSV
df_monthly_counts_cloudy = pd.DataFrame(monthly_counts_cloudy).T
df_monthly_counts_cloudy.index.name = 'Month'
df_monthly_counts_cloudy.reset_index().to_csv(f'{output_folder}monthly_counts_cloudy.csv', index=False)

# Convert hourly_counts to DataFrame, transpose for readability, and save as CSV
df_hourly_counts = pd.DataFrame(hourly_counts).T
df_hourly_counts.index.name = 'Hour'
df_hourly_counts.reset_index().to_csv(f'{output_folder}hourly_counts.csv', index=False)

# Convert monthly_counts to DataFrame, transpose for readability, and save as CSV
df_monthly_counts = pd.DataFrame(monthly_counts).T
df_monthly_counts.index.name = 'Month'
df_monthly_counts.reset_index().to_csv(f'{output_folder}monthly_counts.csv', index=False)

# Convert aggregated_counts to DataFrame, transpose for readability, and save as CSV
df_aggregated_counts = pd.DataFrame(aggregated_counts).T
df_aggregated_counts.index.name = 'Filter'
df_aggregated_counts.reset_index().to_csv(f'{output_folder}aggregated_counts.csv', index=False)

# Convert total_points_by_category to DataFrame and save as CSV
df_total_points_by_category = pd.Series(total_points_by_category, name='Total_Points').to_frame()
df_total_points_by_category.index.name = 'Category'
df_total_points_by_category.reset_index().to_csv(f'{output_folder}total_points_by_category.csv', index=False)

print("CSV files saved successfully.")

#nohup 1498551   
