import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from glob import glob
import pandas as pd

from cropping_functions import compute_global_min_max

# Set the directory containing your NetCDF files
crops_dir = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc/'
output_dir = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/'

channel_name = 'IR_108'
unit = 'Brightness Temperature (K)'

bin_width = 2

#list of paths
crops_paths = sorted(glob(crops_dir+'2013*.nc'))

#check for max min
global_min_max_path = os.path.join(output_dir, 'IR_108_statistics.csv')

# Check if the min-max values are already saved
if os.path.exists(global_min_max_path):
    # Load the vmin and vmax values from the CSV file
    df = pd.read_csv(global_min_max_path)
    # Extract vmin and vmax
    # Extract the Min and Max values
    vmin = df.loc[df['Statistic'] == 'Min', 'Value'].values[0]
    vmax = df.loc[df['Statistic'] == 'Max', 'Value'].values[0]
    # Now you can use vmin and vmax in your code
    print(f"vmin: {vmin}, vmax: {vmax}")
else:
    # Compute max and min for normalizing the colormaps
    vmin, vmax = compute_global_min_max(crops_paths,channel_name)
    print(f'Computed global min: {vmin} and global max: {vmax}')

# Compute the bins for the histgram
bins = np.arange(vmin, vmax + bin_width, bin_width)

# Initialize an empty list to store data from all files
all_data = []

# Loop through each file in the directory
for filename in crops_paths:        
    # Open the NetCDF file
    with xr.open_dataset(filename) as ds:
        # Extract data from a specific variable
        # Replace 'your_variable_name' with the actual variable name
        data = ds[channel_name].values.flatten()
        
        # Remove NaN values and append the data to the list
        all_data.append(data[~np.isnan(data)])

# Concatenate all data into a single array
all_data = np.concatenate(all_data)

# Compute statitistics
percentiles = [5, 25, 50, 75, 95]
percentile_values = np.percentile(all_data, percentiles)

# Create a DataFrame to save the statistics
df_stats = pd.DataFrame({
    'Statistic': ['Min', 'Max'] + [f'{p}th' for p in percentiles],
    'Value': [vmin, vmax] + list(percentile_values)
})

# Save the DataFrame to a CSV file
csv_filename = f'{output_dir}{channel_name}_statistics.csv'
df_stats.to_csv(csv_filename, index=False)

print(f"Statistics saved to {csv_filename}")

# Plot the distribution in log scale
fig, axes = plt.subplots(figsize=(10, 6))
plt.hist(all_data, bins=bins, log=True, color='skyblue')#, edgecolor='black')

# plot the percentiles

for p, val in zip(percentiles, percentile_values):
    plt.axvline(val, color='red', linestyle='--')
    plt.text(val, plt.ylim()[1] * 0.8, f'{p}%', color='red', rotation=90)

plt.xlabel(unit)
plt.ylabel('Counts (Log Scale)')
plt.title(f'Distribution with Percentiles of {channel_name}')
plt.grid(True)
fig.savefig(f'{output_dir}{channel_name}_distribution.png', bbox_inches='tight')
