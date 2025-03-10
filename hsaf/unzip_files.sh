#!/bin/bash

# Define the directory path directly in the script
DIR_PATH="/data/sat/msg/H_SAF/H10/2016"

# Check if the directory exists
if [ ! -d "$DIR_PATH" ]; then
    echo "Directory $DIR_PATH does not exist. Please update the script with a valid path."
    exit 1
fi

# Step 1: Extract all .tar.gz files in the specified directory
echo "Extracting all .tar.gz files in $DIR_PATH..."
for tar_file in "$DIR_PATH"/*.tar.gz; do
    echo "Extracting $tar_file..."
    tar -xzvf "$tar_file" -C "$DIR_PATH"
done

# Step 2: Find and decompress all .gz files matching the pattern 'h10_*_day_merged.H5.gz'
echo "Decompressing .gz files in $DIR_PATH..."
find "$DIR_PATH" -name "h10_*_day_merged.H5.gz" -exec gzip -d {} +

echo "Extraction and decompression completed!"
