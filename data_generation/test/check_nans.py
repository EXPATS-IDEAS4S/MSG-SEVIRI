import os
import xarray as xr
import numpy as np

# Root folder to scan
root_dir = "/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nc"

# Output text file
output_file = "nan_summary.txt" #"/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nan_summary.txt"

# Open the summary file for writing
with open(output_file, "w") as out_f:
    out_f.write("File Path, NaN Count\n")

    # Walk through all subfolders
    for subdir, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".nc"):
                file_path = os.path.join(subdir, file)
                try:
                    ds = xr.open_dataset(file_path, engine='h5netcdf')
                except Exception as e:
                    print(f"Failed to open {file_path}: {e}")
                    continue

                # Count total NaNs across all variables
                nan_count = sum(np.isnan(ds[var]).sum().item() for var in ds.data_vars)

                if nan_count > 0:
                    print(f"{file_path}: {nan_count} NaNs found")
                    out_f.write(f"{file_path}, {nan_count}\n")

                ds.close()

print(f"Summary saved to {output_file}")
