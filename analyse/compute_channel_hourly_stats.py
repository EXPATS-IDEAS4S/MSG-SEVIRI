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
output_path = f"/home/dcorradi/Documents/Fig/channel_distr/{channel}/hourly/"

# Create the output directory if it does not exist
os.makedirs(output_path, exist_ok=True)

# Define the statistics to calculate
percentiles = [5, 25, 50, 75, 95]

# Define bins for the histogram
min_val = 200
max_val = 320
bin_width = 2
bins = np.arange(min_val, max_val + bin_width, bin_width)

def plot_distribution(all_values, bins, channel, hour, output_path, log=False):
    """Plot the distribution of channel values for a specific hour."""
    plt.figure(figsize=(6, 3))
    plt.hist(all_values, bins=bins, density=True, alpha=0.7, color='blue')
    plt.title(f"Distribution of Channel {channel} for Hour {hour:02d}", fontsize=12, fontweight='bold')
    plt.xlabel("Brightness Temperature (K)", fontsize=10)
    plt.ylabel("Density", fontsize=10)
    if log:
        plt.yscale('log')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True)
    if log:
        plt.savefig(f"{output_path}channel_{channel}_distribution_hour_{hour:02d}_log.png", bbox_inches='tight')
    else:
        plt.savefig(f"{output_path}channel_{channel}_distribution_hour_{hour:02d}.png", bbox_inches='tight')

def process_hour(hour, years, months):
    """Process a specific hour across all years and months."""
    all_values = []

    # Iterate over all years and months
    for year in years:
        for month in months:
            month_dir = os.path.join(base_dir, str(year), f"{month:02d}")
            if not os.path.exists(month_dir):
                continue

            # Gather all NetCDF files in the month directory
            nc_files = glob.glob(os.path.join(month_dir, "*.nc"))

            for nc_file in tqdm(nc_files, desc=f"Processing {year}-{month:02d} Hour {hour:02d}"):
                try:
                    # Open the NetCDF file
                    with xr.open_dataset(nc_file) as ds:
                        # Extract the 10.8 channel values for the specified hour
                        if channel in ds and "time" in ds.coords:
                            time_values = ds["time"].values
                            hour_mask = [pd.Timestamp(t).hour == hour for t in time_values]

                            if any(hour_mask):
                                # Select data for the matching hour
                                data = ds[channel].isel(time=hour_mask).values.flatten()
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

        # Create a DataFrame for statistics
        df_stats = pd.DataFrame({
            "min": [min_val],
            "max": [max_val],
            "mean": [mean_val],
            "std": [std_val],
            "hour": [hour]
        })
        for p, v in zip(percentiles, percentile_vals):
            df_stats[f"{p}th percentile"] = v

        print(df_stats)

        # Plot distributions
        plot_distribution(all_values, bins, channel, hour, output_path)
        plot_distribution(all_values, bins, channel, hour, output_path, log=True)

        return df_stats
    else:
        print(f"No data found for hour {hour}.")
        return pd.DataFrame()  # Return an empty DataFrame if no data is found

# Specify the years, months, and hour to process
years = np.arange(2013, 2024)  # Adjust the range as needed
months = np.arange(4, 10)  # All months from January to December
hours = np.arange(0, 24)  # All hours from 00 to 23

# Process all hours and save statistics
all_stats = []
for hour in hours:
    print(f"Processing hour {hour:02d} across years and months.")
    hourly_stats = process_hour(hour, years, months)
    if not hourly_stats.empty:
        all_stats.append(hourly_stats)

# Combine all results into a single DataFrame
if all_stats:
    combined_stats_df = pd.concat(all_stats, ignore_index=True)

    # Save the combined statistics to a CSV file
    combined_stats_df.to_csv(f"{output_path}channel_{channel}_hourly_statistics.csv", index=False)
