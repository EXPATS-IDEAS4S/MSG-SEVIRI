#!/bin/bash

# Define the folder containing the files
SOURCE_FOLDER="/data/sat/msg/H_SAF/H10_nc/2016"

# Check if the folder exists
if [ ! -d "$SOURCE_FOLDER" ]; then
    echo "Error: Source folder does not exist: $SOURCE_FOLDER"
    exit 1
fi

# Loop through all files in the folder
for file in "$SOURCE_FOLDER"/*.nc; do
    # Check if the file exists (in case the folder is empty)
    [ -e "$file" ] || continue

    # Extract the filename
    filename=$(basename "$file")

    # Extract the month from the filename (characters 8-9)
    month=$(echo "$filename" | cut -c9-10)
    echo "month: $month"

    # Skip if the month is not valid (e.g., non-numeric or out of range)
    if ! [[ "$month" =~ ^[0-9]{2}$ ]] || [ "$month" -lt 1 ] || [ "$month" -gt 12 ]; then
        echo "Warning: Skipping file with invalid month: $filename"
        continue
    fi

    # Create the subfolder for the month if it doesn't exist
    target_folder="$SOURCE_FOLDER/$month"
    if [ ! -d "$target_folder" ]; then
        mkdir "$target_folder"
        echo "Created folder: $target_folder"
    fi

    # Move the file to the corresponding subfolder
    mv "$file" "$target_folder/"
    echo "Moved $filename to $target_folder/"
done

echo "File organization completed."
