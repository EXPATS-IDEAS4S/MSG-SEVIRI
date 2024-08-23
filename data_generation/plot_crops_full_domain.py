import os
from glob import glob
import matplotlib.pyplot as plt
import xarray as xr
import pandas as pd 
import numpy as np

# Set the directory containing your NetCDF files of the crops
crops_dir = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc/'

# define path of the MSG data (full domain)
msg_dir = '/data/sat/msg/netcdf/parallax/'

latmax, latmin, lonmax, lonmin = 51.5, 42, 16, 5

# Define parameters
channels = ['IR_039']  # Specify the channel to plot
cmap = 'Greys'       # Colormap
image_format = 'jpeg' # Output image format
scale = '5th-95th'

# Path to Cloud Mask
cma_dir = '/data/sat/msg/CM_SAF/merged_cloud_properties/' #None if you don't want to plot CMA

def find_vmin_vmax(channels, stat_min, stat_max):
    if len(channels) == 1:
        # Load the statistics CSV file
        stats_path = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/{channels[0]}_statistics.csv'
        stats_df = pd.read_csv(stats_path)

        # Extract vmin and vmax from the CSV file
        vmin = stats_df.loc[stats_df['Statistic'] == stat_min, 'Value'].values[0]
        vmax = stats_df.loc[stats_df['Statistic'] == stat_max, 'Value'].values[0]
    elif len(channels) == 2:
        # Load statistics for both channels
        stats_path_1 = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/{channels[0]}_statistics.csv'
        stats_df_1 = pd.read_csv(stats_path_1)
        
        stats_path_2 = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/{channels[1]}_statistics.csv'
        stats_df_2 = pd.read_csv(stats_path_2)

        # Calculate global vmin and vmax across both channels
        vmin = (stats_df_1.loc[stats_df_1['Statistic'] == stat_min, 'Value'].values[0])-(stats_df_2.loc[stats_df_2['Statistic'] == stat_max, 'Value'].values[0])
        
        vmax = (stats_df_1.loc[stats_df_1['Statistic'] == stat_max, 'Value'].values[0])-(stats_df_2.loc[stats_df_2['Statistic'] == stat_min, 'Value'].values[0])
    else:
        # Handle cases with more than 2 channels if needed
        raise ValueError("The script currently supports 1 or 2 channels only.")
    
    return vmin, vmax

vmin, vmax = find_vmin_vmax(channels, scale.split('-')[0], scale.split('-')[1])
print(f'vmin: {vmin}, vmax: {vmax}')

# Get the first 10 crop files
crop_files = sorted(glob(os.path.join(crops_dir, '*.nc')))[:100]

# Define output dir and check if exists
if len(channels)==1:
    output_dir = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/full_domain_figs/{channels[0]}_{scale}/'
else:
    output_dir = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/full_domain_figs/{channels[0]}-{channels[1]}_{scale}/'
if not os.path.exists(output_dir):
    # Create the directory if it doesn't exist
    os.makedirs(output_dir)

# Function to extract the date and time from the crop filename
def extract_datetime(filename):
    basename = os.path.basename(filename)
    date_str, time_str, *_ = basename.split('_')
    return date_str, time_str

# Iterate through the crop files
for crop_file in crop_files:
    # Extract the datetime from the crop filename
    date_str, time_str = extract_datetime(crop_file)
    
    # Construct the corresponding MSG file path
    year = date_str[:4]
    month = date_str[4:6]
    day = date_str[6:8]
    msg_dir_day = os.path.join(msg_dir, year, month)
    print(msg_dir_day)

    # Construct path to CMA
    cma_dir_day = os.path.join(cma_dir, year, month)
    #print(cma_dir_day)
    
    # Find the corresponding MSG file with the same date and time
    msg_file = os.path.join(msg_dir_day, f'{year}{month}{day}-EXPATS-RG.nc')

    # Find the corresponding CMA file
    cma_file = os.path.join(cma_dir_day, f'MCP_{year}-{month}-{day}_regrid.nc') 
    print(cma_file)
    
    # Check if the MSG file exists
    if not os.path.exists(msg_file):
        print(f'MSG file not found for {date_str} {time_str}')
        continue

    if cma_file and not os.path.exists(cma_file):
        print(f'CMA file not found for {date_str} {time_str}')
        continue

    # open CMA
    ds_cma = xr.open_dataset(cma_file)
    cma_data = ds_cma['cma'].sel(time=f'{year}-{month}-{day}T{time_str.replace(":", ":")}')
    
    # Load the MSG data
    with xr.open_dataset(msg_file) as ds_msg:
        if len(channels) == 1:
            # If there's only one channel, just select the data as before
            if channels[0] in ds_msg:
                channel_data = ds_msg[channels[0]].sel(time=f'{year}-{month}-{day}T{time_str.replace(":", ":")}')
            else:
                print(f'Channel {channels[0]} not found in {msg_file}')
                continue
        elif len(channels) == 2:
            # If there are two channels, compute the difference
            if channels[0] in ds_msg and channels[1] in ds_msg:
                channel_data_1 = ds_msg[channels[0]].sel(time=f'{year}-{month}-{day}T{time_str.replace(":", ":")}')
                channel_data_2 = ds_msg[channels[1]].sel(time=f'{year}-{month}-{day}T{time_str.replace(":", ":")}')
                
                # Compute the difference between the two channels
                channel_data = channel_data_1 - channel_data_2
            else:
                print(f'One or both channels {channels} not found in {msg_file}')
                continue
        else:
            print(f'The script currently supports 1 or 2 channels only.')
            continue

    # Countourn data using CMA

    
    # Plot the data
    fig, ax = plt.subplots(figsize=(500, 500), dpi=1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.imshow(np.flipud(channel_data), cmap=cmap, vmin=vmin, vmax=vmax)
    ax.axis('off')

    if cma_dir:
        ax.contourf(np.flipud(cma_data), levels=[0.5, 1], colors='red', alpha=0.3)
    
    # Save the figure
    if len(channels)==1:
        out_filename = f'{channels[0]}_{date_str}_{time_str}_full_domain_{scale}.{image_format}'
    else:
        out_filename = f'{channels[0]}-{channels[1]}_{date_str}_{time_str}_full_domain_{scale}.{image_format}'

    # Add cma to file name
    if cma_dir:
        out_filename = f'CMA_{out_filename}'
    
    crop_filepath = os.path.join(output_dir, out_filename)
    fig.savefig(crop_filepath, dpi=1, bbox_inches='tight', pad_inches=0)
    plt.close(fig)
    
    print(f'{crop_filepath} is saved')