#!/bin/bash

# Correctly match files and process them
for file in S_NWC_NWP_2023-07-*.grib[0-9]*; do
  # Extract the new name by removing the trailing digits before .grib
  new_name=$(echo "$file" | sed -E 's/(.*grib)[0-9]+$/\1/')

  # Check if the new name is different from the original file name
  if [[ "$file" != "$new_name" ]]; then
    # Rename the file
    mv "$file" "$new_name"
    echo "Renamed $file to $new_name"
  fi
done

echo "Renaming completed."

