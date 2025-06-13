import os
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
from glob import glob
import pandas as pd

from cropping_functions import compute_global_min_max

# Set the directory containing your NetCDF files
crops_dir = '/work/dcorradi/crops/IR_108_2013_200x200_EXPATS_fixed/nc/'
output_dir = '/work/dcorradi/crops/IR_108_2013_200x200_EXPATS_fixed/'
cma_dir = '/work/dcorradi/crops/IR_108_2013_200x200_EXPATS_fixed/nc_clouds/'

channel_name = 'IR_108'
unit = 'Brightness Temperature (K)'

apply_cma = True

bin_width = 2

#list of paths
crops_paths = sorted(glob(crops_dir+'201304*.nc'))
cma_paths = sorted(glob(cma_dir+'201304*.nc'))
print(len(crops_paths))
print(len(cma_paths))


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
    #Compute max and min for normalizing the colormaps
    vmin, vmax = compute_global_min_max(crops_paths,channel_name)
    print(f'Computed global min: {vmin} and global max: {vmax}')

# Compute the bins for the histgram
bins = np.arange(vmin, vmax + bin_width, bin_width)

# Initialize an empty list to store data from all files
all_data = []

# Loop through each file in the directory
for filename, cma_file in zip(crops_paths, cma_paths):        
    # Open the NetCDF file
    ds = xr.open_dataset(filename)
    # Extract data from a specific variable
    # Replace 'your_variable_name' with the actual variable name
    data = ds[channel_name].values.flatten()

    if apply_cma:
        cma_ds = xr.open_dataset(cma_file) 
        # Get the cloud mask and apply it
        cloud_mask = cma_ds['cma'].values.flatten()
        data = np.where(cloud_mask == 1, data, np.nan)
    
    # Filter out NaN values and append to all_data
    clean_data = data[~np.isnan(data)]
    if clean_data.size > 0:  # Append only if there's data
        all_data.append(clean_data)

# Check if there's data to concatenate
if all_data:
    # Concatenate all data into a single array
    all_data = np.concatenate(all_data)
else:
    print("No valid data found to concatenate.")
    exit()

# Compute statitistics
percentiles = [1, 2, 5, 10, 25, 50, 75, 90, 95, 98, 99]
percentile_values = np.percentile(all_data, percentiles)

vmin = np.min(all_data)
vmax = np.max(all_data)

# Create a DataFrame to save the statistics
df_stats = pd.DataFrame({
    'Statistic': ['Min', 'Max'] + [f'{p}th' for p in percentiles],
    'Value': [vmin, vmax] + list(percentile_values)
})

# Plot the distribution in log scale
fig, axes = plt.subplots(figsize=(10, 6))
plt.hist(all_data, bins=bins, log=True, color='skyblue', density=True)#, edgecolor='black')

# plot the percentiles

for p, val in zip(percentiles, percentile_values):
    # Plot vertical lines for the percentile
    plt.axvline(val, color='red', linestyle='--')
    # Calculate the middle of the y-axis range
    y_mid = (plt.ylim()[0] + plt.ylim()[1]) / 2
    # Place the text at the middle of the vertical line
    plt.text(val, y_mid, f'{p}%', color='red', rotation=90, verticalalignment='center')
    #plt.text(val, plt.ylim()[1] * 0.8, f'{p}%', color='red', rotation=90)

plt.xlabel(unit)
plt.ylabel('Density (Log Scale)')
plt.grid(True)
if apply_cma:
    plt.title(f'Distribution and Percentiles of {channel_name} with CMA')
    fig.savefig(f'{output_dir}{channel_name}_CMA_distribution.png', bbox_inches='tight')
    # Save the DataFrame to a CSV file
    df_stats.to_csv(f'{output_dir}{channel_name}_statistics_CMA.csv', index=False)
else:
    plt.title(f'Distribution and Percentiles of {channel_name}')
    fig.savefig(f'{output_dir}{channel_name}_distribution.png', bbox_inches='tight')
    df_stats.to_csv(f'{output_dir}{channel_name}_statistics.csv', index=False)

print(f"Statistics and Plot saved to {output_dir}")