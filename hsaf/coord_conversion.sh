#!/bin/bash

# Define the directory where the geocoder command is located
geocoder_dir='/home/dcorradi/Documents/Codes/MSG-SEVIRI/hsaf/hsaf-snow-geocoder'

# Define the input and output directories
input_dir="/data/sat/msg/H_SAF/H10/2014"
output_dir="/data/sat/msg/H_SAF/H10_WGS84/2014"

# Change to the geocoder directory
cd "$geocoder_dir" || { echo "Failed to change directory to $geocoder_dir"; exit 1; }

# Loop over each .hdf file in the input directory
for input_file in "$input_dir"/*.H5; do
  # Extract the base name of the file (without directory and extension)
  base_name=$(basename "$input_file" .H5)
  
  # Define the output file path with .tif extension
  output_file="$output_dir/${base_name}.tif"
  echo "Processing $input_file -> $output_file"
  
  # Run the geocoder command with the specified parameters and error handling
  if python geocoder_app.py -i "$input_file" -o "$output_file" -p H10 --crs 4326; then
    # Print a success message for each processed file
    echo "Processed $input_file -> $output_file"
  else
    # Log the failure and add to the failed files list
    echo "Failed to process $input_file"
  fi
done
