import os
import numpy as np
import xarray as xr
import glob
from tqdm import tqdm
import matplotlib.pyplot as plt
import pandas as pd

# Directories
msg_base_dir = "/data/sat/msg/netcdf/parallax"
cma_base_dir = "/data/sat/msg/CM_SAF/merged_cloud_properties"
output_path = "/home/dcorradi/Documents/Fig/channel_distr/IR_108/cma_cmsaf/"
os.makedirs(output_path, exist_ok=True)

# Define statistics and histogram bins
percentiles = [5, 25, 50, 75, 95]
min_val = 200
max_val = 320
bin_width = 2
bins = np.arange(min_val, max_val + bin_width, bin_width)

def plot_distributions(clear_values, cloud_values, bins, output_path, title, log=False):
    """Plot distributions of clear and cloud values on the same plot."""
    plt.figure(figsize=(8, 5))
    plt.hist(clear_values, bins=bins, density=True, alpha=0.6, label="Clear", color="green")
    plt.hist(cloud_values, bins=bins, density=True, alpha=0.6, label="Cloud", color="blue")
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel("Brightness Temperature (K)", fontsize=12)
    plt.ylabel("Density", fontsize=12)
    plt.yscale("log" if log else "linear")
    plt.legend(fontsize=10)
    plt.grid(True)
    suffix = "_log" if log else ""
    plt.savefig(f"{output_path}{title.replace(' ', '_').lower()}{suffix}.png", bbox_inches="tight")
    plt.close()

def process_file(msg_file, cma_file):
    """Process an MSG file and its corresponding CMA file."""
    try:
        with xr.open_dataset(msg_file) as ds_msg, xr.open_dataset(cma_file) as ds_cma:
            channel_data = ds_msg["IR_108"]
            cma_mask = ds_cma["cma"]

            # Ensure lat/lon alignment if necessary (assumes exact match here)
            if channel_data.shape != cma_mask.shape:
                raise ValueError("MSG and CMA dimensions do not match.")

            clear_values = channel_data.values[cma_mask.values == 0]
            cloud_values = channel_data.values[cma_mask.values == 1]

            clear_values = clear_values[~np.isnan(clear_values)]
            cloud_values = cloud_values[~np.isnan(cloud_values)]

            # Compute statistics
            clear_stats = {
                "min": np.min(clear_values),
                "max": np.max(clear_values),
                "mean": np.mean(clear_values),
                "std": np.std(clear_values),
                **{f"{p}th_percentile": np.percentile(clear_values, p) for p in percentiles},
                "category": "Clear",
            }
            cloud_stats = {
                "min": np.min(cloud_values),
                "max": np.max(cloud_values),
                "mean": np.mean(cloud_values),
                "std": np.std(cloud_values),
                **{f"{p}th_percentile": np.percentile(cloud_values, p) for p in percentiles},
                "category": "Cloud",
            }

            return clear_stats, cloud_stats, clear_values, cloud_values

    except Exception as e:
        print(f"Error processing files {msg_file} and {cma_file}: {e}")
        return None, None, None, None

def process_year(year, month):
    """Process MSG and CMA files for a specific year."""
    #stats_combined = []
    #clear_all_values = []
    #cloud_all_values = []

    msg_dir = os.path.join(msg_base_dir, str(year), f"{month:02d}")
    cma_dir = os.path.join(cma_base_dir, str(year), f"{month:02d}")
    print(msg_dir)
    print(cma_dir)

    if not os.path.exists(msg_dir) or not os.path.exists(cma_dir):
        print(f"Skipping month {month:02d}: Missing data directory.")
        return None 

    msg_files = sorted(glob.glob(os.path.join(msg_dir, "**", "*.nc"), recursive=True))
    cma_files = sorted(glob.glob(os.path.join(cma_dir, "**", "*.nc"), recursive=True))
    print(len(msg_files))
    print(len(cma_files))

    if len(msg_files) != len(cma_files):
        print(f"Skipping month {month:02d}: Number of files do not match.")
        return None


    for msg_file, cma_file in tqdm(zip(msg_files, cma_files), total=len(msg_files)):
        
        clear_stats, cloud_stats, clear_values, cloud_values = process_file(msg_file, cma_file)

        if clear_stats and cloud_stats:
            stats_combined.extend([clear_stats, cloud_stats])
            clear_all_values.extend(clear_values)
            cloud_all_values.extend(cloud_values)

    # Save statistics to CSV
    df_stats = pd.DataFrame(stats_combined)
    df_stats.to_csv(f"{output_path}channel_ir_108_cma_statistics_{year}.csv", index=False)

    # Plot overall distributions for the year
    plot_distributions(
        clear_all_values, cloud_all_values, bins, output_path,
        title=f"Brightness Temperature Distribution for {year}-{month:02d}", log=False
    )
    plot_distributions(
        clear_all_values, cloud_all_values, bins, output_path,
        title=f"Brightness Temperature Distribution for {year}-{month:02d} (Log Scale)", log=True
    )

# Run for the year 2013
months = range(4, 10)
for month in months:
    process_year(2013, month)

# nohup 