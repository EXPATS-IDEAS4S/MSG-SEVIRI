#!/bin/bash

: '
Extracts .zip files from a specified source directory to a target directory.

Usage:
  ./extract_zip.sh [zip_files_dir] [output_dir]

Arguments:
  zip_files_dir (Optional): The directory containing the .zip files to be extracted.
                            If not provided, a default directory is used.
  output_dir    (Optional): The directory where the .zip files will be extracted to.
                            If not provided, a default directory is used.

Defaults:
  zip_files_dir: "/work/MSG/HRIT/2023/07/"
  output_dir:    "/work/NWC_GEO/import/Sat_data/"

Options:
  delete_zip_after_extraction: Configures whether the .zip files should be deleted after extraction.
                               Set to "true" to enable deletion, "false" to keep the .zip files.

Details:
  The script navigates to the "zip_files_dir", iterates over each .zip file that matches
  the pattern "EPCT_HRSEVIRI_*.zip", and extracts its contents to "output_dir". Optionally,
  it can delete the original .zip file after successful extraction based on the
  "delete_zip_after_extraction" setting.

Examples:
  To extract using default directories without passing any arguments:
    ./extract_zip.sh

  To specify custom directories:
    ./extract_zip.sh "/custom/zip/files/dir/" "/custom/output/dir/"

Note:
  Ensure the specified directories exist and you have the necessary permissions to read
  from the source directory and write to the target directory.
'

# Check for command-line arguments and use them if provided; otherwise, use default values
zip_files_dir="${1:-'/work/MSG/HRIT/2023/07/'}" # Default zip files directory
output_dir="${2:-'/work/NWC_GEO/import/Sat_data/'}" # Default output directory

# Configure whether to delete the zip files after extraction (true or false)
delete_zip_after_extraction=true

# Navigate to the directory containing the zip files
if cd "$zip_files_dir"; then
    # Loop through each zip file matching the pattern and extract it to the output directory
    for file in EPCT_HRSEVIRI_*.zip; do
        unzip -o "$file" -d "$output_dir"
        
        # Check if delete_zip_after_extraction is set to true
        if [ "$delete_zip_after_extraction" = true ]; then
            echo "Deleting zip file: $file"
            rm "$file"
        fi
    done
else
    echo "The specified zip files directory does not exist: $zip_files_dir"
    exit 1
fi
