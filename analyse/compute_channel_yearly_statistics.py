import os
import numpy as np
import xarray as xr
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd

# Define the base directory for the NetCDF files
base_dir = "/data/sat/msg/netcdf/parallax"

# Define the channel to process
channel = "IR_108"

# Path to save the output plots
output_path = f"/home/dcorradi/Documents/Fig/channel_distr/{channel}/"

# create directory if it does not exist
os.makedirs(output_path, exist_ok=True)

# Define the statistics to calculate
percentiles = [5, 25, 50, 75, 95]

# Define bins for the histogram
min_val = 200
max_val = 320
bin_width = 2
bins = np.arange(min_val, max_val + bin_width, bin_width)

def plot_distribution(all_values, bins, channel, year, output_path, log=False):
    # Plot the distribution shape
    plt.figure(figsize=(6, 3))
    plt.hist(all_values, bins=bins, density=True, alpha=0.7, color='blue')
    plt.title(f"Distribution of Channel {channel} in {year}", fontsize=12, fontweight='bold')
    plt.xlabel("Brightness Temperature (K)", fontsize=10)
    plt.ylabel("Density", fontsize=10)
    if log:
        plt.yscale('log')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True)
    if log:
        plt.savefig(f"{output_path}channel_{channel}_distribution_{year}_log.png", bbox_inches='tight')
    else:
        plt.savefig(f"{output_path}channel_{channel}_distribution_{year}.png", bbox_inches='tight')

def process_year(year):
    """Process all NetCDF files for a given year and calculate statistics."""
    year_dir = os.path.join(base_dir, str(year))
    all_values = []

    # Iterate through months
    for month in range(4, 10):
        month_dir = os.path.join(year_dir, f"{month:02d}")
        print(month_dir)
        if not os.path.exists(month_dir):
            continue

        # Gather all NetCDF files in the month directory
        nc_files = glob.glob(os.path.join(month_dir, "*.nc"))

        for nc_file in tqdm(nc_files, desc=f"Processing {year}-{month:02d}"):
            try:
                # Open the NetCDF file
                with xr.open_dataset(nc_file) as ds:
                    # Extract the 10.8 channel values
                    if channel in ds:
                        data = ds[channel].values.flatten()
                        # Remove NaNs and append to the list
                        all_values.extend(data[~np.isnan(data)])
            except Exception as e:
                print(f"Error processing file {nc_file}: {e}")

    # Convert collected values to a NumPy array for statistics
    all_values = np.array(all_values)

    if len(all_values) > 0:
        # Calculate statistics
        min_val = np.min(all_values)
        max_val = np.max(all_values)
        mean_val = np.mean(all_values)
        std_val = np.std(all_values)
        percentile_vals = np.percentile(all_values, percentiles)
        # Put statistics in a dataframe
        df_stats = pd.DataFrame({"min": [min_val],"max": [max_val],"mean": [mean_val],"std": [std_val], "year": [year]})
        for p, v in zip(percentiles, percentile_vals):
            df_stats[f"{p}th percentile "] = v      
        print(df_stats)
        plot_distribution(all_values, bins, channel, year, output_path)
        plot_distribution(all_values, bins, channel, year, output_path, log=True)
        
    else:
        print(f"No data found for year {year}.")

    return df_stats


# Specify the years to process
years = np.arange(2013, 2024)  # Adjust the range as needed
print(f"Processing years: {years}")

all_stats = []
for year in years:
    df_stats = process_year(year)
    all_stats.append(df_stats)

# Combine all results into a single DataFrame
combined_stats_df = pd.concat(all_stats, index=False)

#save the combined dataframe to a CSV file
combined_stats_df.to_csv(f"{output_path}channel_{channel}_yearly_statistics.csv")


# nohup 996255