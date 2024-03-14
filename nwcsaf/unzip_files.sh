#!/bin/bash

# Specify the directory containing the zip files
zip_files_dir='/work/MSG/HRIT/2023/07/'

# Specify the directory where you want to extract the contents
output_dir='/work/NWC_GEO/import/Sat_data/'

# Configure whether to delete the zip files after extraction (true or false)
delete_zip_after_extraction=true

# Navigate to the directory containing the zip files
cd "$zip_files_dir"

# Loop through each zip file matching the pattern and extract it to the output directory
for file in EPCT_HRSEVIRI_*.zip; do
    unzip -o "$file" -d "$output_dir"
    
    # Check if delete_zip_after_extraction is set to true
    if [ "$delete_zip_after_extraction" = true ]; then
        echo "Deleting zip file: $file"
        rm "$file"
    fi
done