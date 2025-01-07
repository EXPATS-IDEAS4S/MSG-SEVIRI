import os
import numpy as np
import xarray as xr
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt

# Define the base directory for the NetCDF files
base_dir = "/data/sat/msg/netcdf/parallax"

# Define the channel to process
channel = "IR_108"

# Define the statistics to calculate
percentiles = [5, 25, 50, 75, 95]

def process_year(year):
    """Process all NetCDF files for a given year and calculate statistics."""
    year_dir = os.path.join(base_dir, str(year))
    print(year_dir)
    all_values = []

    # Iterate through months
    for month in range(4, 10):
        month_dir = os.path.join(year_dir, f"{month:02d}")
        print(month_dir)
        if not os.path.exists(month_dir):
            continue

        # Gather all NetCDF files in the month directory
        nc_files = glob.glob(os.path.join(month_dir, "*.nc"))
        print(nc_files)

        for nc_file in tqdm(nc_files, desc=f"Processing {year}-{month:02d}"):
            try:
                # Open the NetCDF file
                with xr.open_dataset(nc_file) as ds:
                    # Extract the 10.8 channel values
                    if channel in ds:
                        print(ds)
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
        median_val = np.median(all_values)
        percentile_vals = np.percentile(all_values, percentiles)

        # Display statistics
        print(f"Statistics for year {year}:")
        print(f"  Min: {min_val}, Max: {max_val}")
        print(f"  Mean: {mean_val}, Median: {median_val}")
        for p, v in zip(percentiles, percentile_vals):
            print(f"  {p}th Percentile: {v}")

        # Plot the distribution shape
        plt.figure(figsize=(10, 6))
        plt.hist(all_values, bins=100, density=True, alpha=0.7, color='blue')
        plt.title(f"Distribution of Channel {channel} Values in {year}")
        plt.xlabel("Value")
        plt.ylabel("Density")
        plt.grid(True)
        plt.show()
    else:
        print(f"No data found for year {year}.")


# Specify the years to process
years = np.arange(2013, 2024)  # Adjust the range as needed
print(f"Processing years: {years}")

for year in years:
    process_year(year)


