import os
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

from plotting_functions import plot_single_map

# Define paths and channels
msg_folder = '/data/sat/msg/netcdf/parallax/2023/07/'
output_folder = '/home/dcorradi/Documents/Fig/summer_school/'
filename = '20230709-EXPATS-RG.nc'  # Example NetCDF filename
file_path = os.path.join(msg_folder, filename)
channel = 'VIS006'  # The channel you're interested in (you can change this)
time_range = [15, 17]  # Hours from 15:00 to 17:00 (included)

# Open the NetCDF file
ds = xr.open_dataset(file_path)

# Assuming the dataset has the following dimensions: time, lon, lat, and channels
# Filter the dataset to include only the time range of interest (15:00 to 17:00 UTC)
start_time = np.datetime64(datetime.strptime('2023-07-09 15:00', '%Y-%m-%d %H:%M'))
end_time = np.datetime64(datetime.strptime('2023-07-09 19:00', '%Y-%m-%d %H:%M'))
time_selection = ds.sel(time=slice(start_time, end_time))

# Extract the channel of interest (IR_108) - modify according to your actual data structure
channel_data = time_selection[channel]

# Calculate min and max across all time steps for normalization
data_min = channel_data.min().item()  # Get the minimum value
data_max = channel_data.max().item()  # Get the maximum value

# Now you can use these values to normalize your colormap
norm = plt.Normalize(vmin=data_min, vmax=data_max)  # Linear normalization

# Assuming the data contains lat and lon dimensions, or extract separately if needed
lon = ds['lon'].values
lat = ds['lat'].values

# Loop over the selected time range and plot maps
for t in channel_data.time:
    # Extract data for a specific time
    data_at_time = channel_data.sel(time=t).values
    #print(data_at_time)
    
    # Create a string representation of the time for plot labeling
    date_time_str = np.datetime_as_string(t, unit='m')
    print(date_time_str)
    # Set color map, normalization, and extent (these need to be adapted to your needs)
    cmap = 'gray'  # Choose an appropriate colormap
    extent = [7, 10, 46.5, 49.5]  # Global extent, adjust based on data #[left, right, bottom ,top]

    # Define the data name string and label (modify according to your variable of interest)
    data_name_str = f'{channel}'
    label = f'{channel} Reflectances (%)'  # Example label for IR channels

    # Plot the map using your existing function
    plot_single_map(data_at_time, lon, lat, cmap, norm, extent, date_time_str, data_name_str, label, path_fig=output_folder)
    
    print(f"Plot saved for {date_time_str}")

#8.487149, 48,056274 coordinate of radar
#8.42 8.54, 48, 48.10