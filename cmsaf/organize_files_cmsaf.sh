##!/bin/bash

# This script sorts files from a specified directory into subfolders based on month and day extracted
# from the file's name. It is designed specifically for files with names including a datetime string
# like CMAin20230401000000405SVMSGI1UD.nc/CTXin20230401000000405SVMSGI1UD.nc where `20230401` is extracted for sorting.
#
# Usage:
# bash organize_files_cmsaf.sh /path/to/your/folder
#
# Parameters:
# $1 - The path to the directory containing files to be sorted.
#
# Assumptions:
# - Files to be sorted are directly within the specified directory.
# - Filenames contain the date in the format YYYYMMDD.
# - The script has permissions to create directories and move files within the specified path.

# Check if a folder path was provided
if [ -z "$1" ]; then
    echo "Please provide a folder path."
    exit 1
fi

folder_path=$1

# Navigate to the specified folder
cd "$folder_path" || exit

# Loop through files matching the expected pattern
for file in C*in????????*.nc; do
    # Extract the date string from the filename using grep to capture YYYYMMDD following 'in'
    date_str=$(echo "$file" | grep -oP '(?<=in)\d{8}')

    if [ -n "$date_str" ]; then
        # Extract year, month, and day from the date string
        #year=${date_str:0:4}
        month=${date_str:4:2}
        day=${date_str:6:2}

        # Create the directory path for year, month, and day
        dir_path="${month}/${day}"

        # Check if the directory exists, if not, create it
        mkdir -p "$dir_path"

        # Move the file into the corresponding subfolder
        mv "$file" "$dir_path/"
    fi
done
