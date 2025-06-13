import numpy as np
import os
import glob

# Path to .npy files
train_path = '/data1/crops/npy_crops_test/'
train_files = sorted(glob.glob(os.path.join(train_path+'1/', "*.npy")))

if not train_files:
    raise ValueError("No .npy files found in the specified directory!")

print(f"Found {len(train_files)} .npy files in the directory.")

# Loop over the files and if contains Nan values, delete it
for file in train_files:
    print(f"Processing file '{file}'...")
    npy_array = np.load(file)  # Shape: (channels, height, width)

    #Check if the file has any NaN values
    if np.isnan(npy_array).any():
        print(f"Deleting file '{file}' due to NaN values.")
        os.remove(file)