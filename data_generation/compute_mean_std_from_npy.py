import numpy as np
import os
import glob

# Path to .npy files
train_path = '/data1/crops/npy_crops_test/'
train_files = sorted(glob.glob(os.path.join(train_path+'1/', "*.npy")))

if not train_files:
    raise ValueError("No .npy files found in the specified directory!")

print(f"Found {len(train_files)} .npy files in the directory.")

# Load a sample file to determine the number of channels
sample_array = np.load(train_files[0])  # Shape: (channels, height, width)
num_channels, x_pixels, y_pixels = sample_array.shape

# Initialize accumulators
channel_sums = np.zeros(num_channels)
channel_squares = np.zeros(num_channels)

num_pixels = len(train_files) * x_pixels * y_pixels  # Total number of pixels across all images

# Compute mean and standard deviation in a single pass
for file in train_files:
    print(f"Processing file '{file}'...")
    npy_array = np.load(file)  # Shape: (channels, height, width)

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

# Save results as .npy files
np.save(os.path.join(train_path, 'mean.npy'), channel_means)
np.save(os.path.join(train_path, 'std.npy'), channel_stds)