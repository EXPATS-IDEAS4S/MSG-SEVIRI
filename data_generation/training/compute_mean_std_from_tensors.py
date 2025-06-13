import numpy as np
import os
import glob
import xarray as xr

# Path to .npy files
file_extension = 'nc'
crop_path = f'/data1/crops/dcv2_ir108_100x100_test_tensor/{file_extension}/'
crop_files = sorted(glob.glob(os.path.join(crop_path+'1/', "*."+file_extension)))

if not crop_files:
    raise ValueError(f"No {file_extension} files found in the specified directory!")

print(f"Found {len(crop_files)} {file_extension} files in the directory.")

# Load a sample file to determine the number of channels
def open_file(file, file_extension):
    if file_extension == 'nc':
        return xr.open_dataarray(file, engine="h5netcdf").values  # Using xarray for .nc files
    elif file_extension == 'npy':
        return np.load(file)  # Shape: (channels, height, width)
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

sample_array = open_file(crop_files[0], file_extension)
num_channels, x_pixels, y_pixels = sample_array.shape

# Initialize accumulators
channel_sums = np.zeros(num_channels)
channel_squares = np.zeros(num_channels)

num_pixels = len(crop_files) * x_pixels * y_pixels  # Total number of pixels across all images

# Compute mean and standard deviation in a single pass
for file in crop_files:
    print(f"Processing file '{file}'...")
    npy_array = open_file(file, file_extension)

    #Check if the file has all nan values
    if np.isnan(npy_array).all():
        print(f"Skipping file '{file}' due to NaN values.")
        continue
    
    # Sum for mean and squared sum for std excluding nan values
    for c in range(num_channels):
        channel_sums[c] += np.nansum(npy_array[c, :, :])
        channel_squares[c] += np.nansum(npy_array[c, :, :] ** 2)

# Compute mean and std
channel_means = channel_sums / num_pixels
channel_stds = np.sqrt((channel_squares / num_pixels) - (channel_means ** 2))

# Print results with only 3 decimals
print(f"Mean per channel: {channel_means}")
print(f"Std per channel: {channel_stds}")

# Save mean and std together in a txt files
mean_std_path = f'{crop_path}mean_std.txt'
with open(mean_std_path, 'w') as f:
    f.write("Mean per channel:\n")
    f.write(' '.join([f"{mean:.3f}" for mean in channel_means]) + '\n')
    f.write("Std per channel:\n")
    f.write(' '.join([f"{std:.3f}" for std in channel_stds]) + '\n')
print(f"Mean and standard deviation saved to {mean_std_path}")