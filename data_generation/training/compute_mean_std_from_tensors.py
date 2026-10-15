"""
Compute mean and standard deviation for selected channels in a dataset of .nc or .npy files.

This script:
1. Loads a list of crop files from a specified directory.
2. Selects channels either by variable name (for .nc files) or all channels (for .npy files).
3. Handles both 3D arrays (C, H, W) and 4D arrays (C, T, H, W) where T is a time dimension.
4. Computes mean and standard deviation for each selected channel over all spatial and temporal pixels.
5. Skips files with all NaN values.
6. Saves the computed statistics in a text file along with the list of channels used.

Parameters (set in CONFIG section):
- file_extension: str
    Either 'nc' for NetCDF files or 'npy' for NumPy arrays.
- crop_path: str
    Base directory containing subfolders with crop files.
- search_dir: str
    Specific subdirectory containing the files to process.
- selected_channel_names: list[str] or None
    Names of channels to process for .nc files.
    If None, all available variables in the file are used.

Outputs:
- Prints statistics to stdout.
- Saves results to a 'mean_std_selected.txt' file in the crop_path.
"""

import numpy as np
import os
import glob
import xarray as xr

# ================= CONFIG =================
file_extension = 'nc'  # 'nc' or 'npy'
crop_path = f'/data1/crops/clips_ir108_100x100_8frames_2013-2020/{file_extension}/'
search_dir = os.path.join(crop_path, '1')  # Subfolder containing the files

# Select channels by name (for .nc files)
# If None → all variables are used
selected_channel_names = ["IR_108_cm"]
# ===========================================

# ----------------- File Finder -----------------
crop_files = sorted(glob.glob(os.path.join(search_dir, f"*.{file_extension}")))
if not crop_files:
    raise ValueError(f"No {file_extension} files found in: {search_dir}")
print(f"Found {len(crop_files)} {file_extension} files.")

# ----------------- File Loader -----------------
def open_nc(file_path):
    return xr.open_dataset(file_path)#, engine="h5netcdf")

def open_npy(file_path):
    return np.load(file_path)

# ----------------- Detect channels -----------------
sample_file = crop_files[0]
if file_extension == 'nc':
    ds = open_nc(sample_file)
    all_channel_names = list(ds.data_vars)
    print(f"Available channels: {all_channel_names}")
    
    if selected_channel_names is None:
        selected_channel_names = all_channel_names
    else:
        missing = [ch for ch in selected_channel_names if ch not in all_channel_names]
        if missing:
            raise ValueError(f"Requested channels not found: {missing}")
    
    print(f"Using channels: {selected_channel_names}")
    sample_array = ds[selected_channel_names].to_array().values  # (C, T?, H, W)
else:
    arr = open_npy(sample_file)
    sample_array = arr

# Handle shape
if sample_array.ndim == 4:
    num_channels, T, H, W = sample_array.shape
    has_time = True
elif sample_array.ndim == 3:
    num_channels, H, W = sample_array.shape
    T = 1
    has_time = False
else:
    raise ValueError(f"Unexpected array shape: {sample_array.shape}")

print(f"Detected shape: channels={num_channels}, time={T if has_time else 'none'}, height={H}, width={W}")

# ----------------- Accumulators -----------------
channel_sums = np.zeros(num_channels, dtype=np.float64)
channel_squares = np.zeros(num_channels, dtype=np.float64)
total_pixels = 0

# ----------------- Processing -----------------
for file in crop_files:
    print(f"Processing: {file}")
    
    if file_extension == 'nc':
        ds = open_nc(file)
        arr = ds[selected_channel_names].to_array().values
    else:
        arr = open_npy(file)
    
    if np.isnan(arr).all():
        print(f"Skipping file '{file}' (all NaN).")
        continue

    if arr.ndim == 3:
        arr = arr[:, np.newaxis, :, :]  # → (C, T=1, H, W)

    C, T, H, W = arr.shape
    total_pixels += T * H * W

    for c in range(C):
        valid_data = arr[c, :, :, :]
        channel_sums[c] += np.nansum(valid_data)
        channel_squares[c] += np.nansum(valid_data ** 2)

# ----------------- Mean & Std -----------------
channel_means = channel_sums / total_pixels
channel_stds = np.sqrt((channel_squares / total_pixels) - (channel_means ** 2))

print(f"Mean (selected channels): {channel_means}")
print(f"Std  (selected channels): {channel_stds}")

# ----------------- Save -----------------
mean_std_path = os.path.join(crop_path, 'mean_std_selected.txt')
with open(mean_std_path, 'w') as f:
    f.write(f"Selected channels: {selected_channel_names}\n")
    f.write("Mean per channel:\n")
    f.write(' '.join([f"{mean:.3f}" for mean in channel_means]) + '\n')
    f.write("Std per channel:\n")
    f.write(' '.join([f"{std:.3f}" for std in channel_stds]) + '\n')

print(f"✅ Mean and standard deviation saved to: {mean_std_path}")
