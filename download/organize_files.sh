#!/bin/bash

# This script sorts files from a specified directory into subfolders based on the day extracted
# from the file's name. It is designed specifically for files with names following the structure:
# MSG3-SEVI-MSG15-0100-NA-YYYYMMDDHHMMSS.something
# where YYYYMMDDHHMMSS is a datetime string from which the day (DD) is extracted.
#
# Usage:
# bash sort_files_by_day.sh /path/to/your/folder
#
# Parameters:
# $1 - The path to the directory containing files to be sorted.
#
# Assumptions:
# - Files to be sorted are directly within the specified directory.
# - Filenames strictly follow the given structure.
# - The script has permissions to create directories and move files within the specified path.


# Check if a folder path was provided
if [ -z "$1" ]; then
    echo "Please provide a folder path."
    exit 1
fi

folder_path=$1

# Navigate to the specified folder
cd "$folder_path" || exit

# Loop through files matching the specific structure
#for file in MSG*-SEVI-MSG15-0100-NA-*.subset.nat; do
for file in MSG*; do
    # Extract the date string from the filename
    date_str=$(echo "$file" | grep -oP '\d{14}')

    if [ -n "$date_str" ]; then
        # Extract the day from the date string
        day=${date_str:6:2}

        # Check if the subfolder for the day exists, if not, create it
        if [ ! -d "$day" ]; then
            mkdir "$day"
        fi

        # Move the file into the corresponding subfolder
        mv "$file" "$day"/
    fi
done
