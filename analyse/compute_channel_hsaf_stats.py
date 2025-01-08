import os
import numpy as np
import xarray as xr
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd

# Define the directories
base_dir = "/data/sat/msg/netcdf/parallax"
hsaf_dir = "/data/sat/msg/H_SAF/H10_nc"

# Define the channel to process
channel = "IR_108"

# Path to save the output plots
output_path = f"/home/dcorradi/Documents/Fig/channel_distr/{channel}/hsaf/"

# Create the output directory if it does not exist
os.makedirs(output_path, exist_ok=True)

# HSAF category labels
CATEGORY_LABELS = {
    0: "Snow",
    42: "Cloud",
    85: "Land",
    170: "Sea",
    212: "Dark",
    233: "No Data",
    255: "Space",
}

# Define statistics to calculate
percentiles = [5, 25, 50, 75, 95]

# Define bins for the histogram
min_val = 200
max_val = 320
bin_width = 2
bins = np.arange(min_val, max_val + bin_width, bin_width)

def plot_distribution(values, bins, category_label, output_path, log=False):
    """Plot the distribution of channel values for a specific HSAF category."""
    plt.figure(figsize=(6, 3))
    plt.hist(values, bins=bins, density=True, alpha=0.7, color='blue')
    plt.title(f"Distribution for {category_label} from HSAF", fontsize=12, fontweight='bold')
    plt.xlabel("Brightness Temperature (K)", fontsize=10)
    plt.ylabel("Density", fontsize=10)
    if log:
        plt.yscale('log')
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.grid(True)
    if log:
        plt.savefig(f"{output_path}distribution_hasf_{category_label}_log.png", bbox_inches='tight')
    else:
        plt.savefig(f"{output_path}distribution_hsaf_{category_label}.png", bbox_inches='tight')

def process_file(msg_file, hsaf_file):
    """Process a single MSG file and its corresponding HSAF file."""
    try:
        with xr.open_dataset(msg_file) as ds_msg, xr.open_dataset(hsaf_file) as ds_hsaf:
            # Extract the channel data

            channel_data = ds_msg[channel]
            lat_msg, lon_msg = ds_msg["lat"].values, ds_msg["lon"].values

            # Extract HSAF category data
            hsaf_category = ds_hsaf["CATEGORY"].values
            lat_hsaf, lon_hsaf = ds_hsaf["latitude"].values, ds_hsaf["longitude"].values

            results = {}

            # Loop over HSAF categories
            for category, label in CATEGORY_LABELS.items():
                mask = hsaf_category == category
                if not np.any(mask):
                    continue

                # Extract lat/lon of HSAF for this category
                lat_subset = lat_hsaf[mask]
                lon_subset = lon_hsaf[mask]

                # Find corresponding MSG channel values
                matched_values = []
                for lat, lon in zip(lat_subset, lon_subset):
                    # Find the closest MSG pixel
                    distance = (lat_msg - lat) ** 2 + (lon_msg - lon) ** 2
                    closest_idx = np.unravel_index(distance.argmin(), distance.shape)
                    closest_value = channel_data.values[closest_idx]
                    if not np.isnan(closest_value):
                        matched_values.append(closest_value)

                matched_values = np.array(matched_values)
                if matched_values.size > 0:
                    # Calculate statistics
                    stats = {
                        "min": np.min(matched_values),
                        "max": np.max(matched_values),
                        "mean": np.mean(matched_values),
                        "std": np.std(matched_values),
                        **{f"{p}th_percentile": np.percentile(matched_values, p) for p in percentiles},
                    }
                    results[label] = {"values": matched_values, "stats": stats}
    except Exception as e:
        print(f"Error processing file pair {msg_file} and {hsaf_file}: {e}")
        return {}

    return results

def process_year_month(year, month):
    """Process all MSG files for a given year and month with corresponding HSAF files."""
    msg_dir = os.path.join(base_dir, str(year), f"{month:02d}")
    hsaf_dir_month = os.path.join(hsaf_dir, str(year), f"{month:02d}")
    if not os.path.exists(msg_dir) or not os.path.exists(hsaf_dir_month):
        print(f"Skipping year {year}, month {month}: Missing data directory.")
        return []

    results = []

    # Get MSG and HSAF files
    msg_files = sorted(glob.glob(os.path.join(msg_dir, "*.nc")))
    hsaf_files = sorted(glob.glob(os.path.join(hsaf_dir_month, "*.nc")))

    # Process MSG-HSAF pairs
    for msg_file in tqdm(msg_files, desc=f"Processing {year}-{month:02d}"):
        # Find the corresponding HSAF file (same date)
        msg_date = os.path.basename(msg_file).split("_")[1]  # Adjust based on naming convention
        hsaf_file = next((f for f in hsaf_files if msg_date in os.path.basename(f)), None)
        if not hsaf_file:
            print(f"No matching HSAF file found for {msg_file}")
            continue

        results.append(process_file(msg_file, hsaf_file))

    return results

# Process all years and months
years = range(2013, 2024)
months = range(4, 10)

all_results = []

for year in years:
    for month in months:
        print(f"Processing year {year}, month {month}")
        results = process_year_month(year, month)
        all_results.extend(results)

# Consolidate and save statistics
stats_combined = []

for result in all_results:
    for category, data in result.items():
        stats = data["stats"]
        stats["category"] = category
        stats_combined.append(stats)

df_stats = pd.DataFrame(stats_combined)
df_stats.to_csv(f"{output_path}channel_{channel}_hsaf_statistics.csv", index=False)

# Plot distributions
for result in all_results:
    for category, data in result.items():
        plot_distribution(data["values"], bins, category, output_path)
        plot_distribution(data["values"], bins, category, output_path, log=True)

