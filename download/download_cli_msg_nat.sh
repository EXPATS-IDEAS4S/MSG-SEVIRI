#!/bin/bash

: '
Usage: to be run from /Documents/Github/EXPATS/MSG-SEVIRI/
command: bash download/download_cli.sh [START_TIME] [END_TIME] [DOWNLOAD_DIR]

This script downloads satellite data for a specified time range using the EUMETSAT Data Access API.
The start time, end time, and download directory are optional command-line arguments. 
If not provided, default values are used:
- START_TIME: Optional. The start time for the data retrieval, formatted as "YYYY-MM-DDTHH:MM".
- END_TIME: Optional. The end time for the data retrieval, formatted as "YYYY-MM-DDTHH:MM". 
- DOWNLOAD_DIR: Optional. The directory where the downloaded files will be saved. 

Before downloading, the script fetches necessary credentials using a separate Python script (credentials.py) 
and sets them for the current session.

Parameters:
- PRODUCT: Specifies the satellite product to download.
- FORMAT: Defines the format of the downloaded data. Supported formats include 'hrit', 'msgnative', and 'netcdf4'.
- ROI (Region of Interest): Optional parameter to specify the geographic bounding box for the data, formatted as 
[North, South, West, East] coordinates.

The script sets the credentials for data access and then proceeds with the data download process for the specified product, time range, format, and saves the downloaded files to the specified or default download directory.

Examples:
- To use default START_TIME, END_TIME, and DOWNLOAD_DIR:
  ./download_script.sh

- To specify custom START_TIME, END_TIME, and DOWNLOAD_DIR:
  ./download_script.sh "2023-08-01T00:00" "2023-08-16T00:00" "/custom/download/dir"

Note: Ensure that the credentials.py script is present in the same directory as this script and that it outputs the consumer key and secret as space-separated values.
'


# Default values for START_TIME, END_TIME, and DOWNLOAD_DIR
default_start_time="2023-08-01T00:00"
default_end_time="2023-08-02T00:00"
default_download_dir="/data/sat/msg/nat/incoming/"

# Use command-line arguments if provided, otherwise use default values
START_TIME="${1:-$default_start_time}"
END_TIME="${2:-$default_end_time}"
DOWNLOAD_DIR="${3:-$default_download_dir}"

echo "Using START_TIME: $START_TIME"
echo "Using END_TIME: $END_TIME"
echo "Downloading to: $DOWNLOAD_DIR"

# Start time for the script execution, not to be confused with the data start time
script_start_time=$(date +%s)

# Execute the Python script to get credentials
credentials=$(python3 readers/credentials.py)

# Use an array to split the credentials output
readarray -td' ' cred_array <<<"$credentials"; declare -p cred_array
ConsumerKey=${cred_array[0]}
ConsumerSecret=${cred_array[1]}

# Trim possible trailing newline
ConsumerKey=$(echo $ConsumerKey | tr -d '\n')
ConsumerSecret=$(echo $ConsumerSecret | tr -d '\n')

eumdac set-credentials $ConsumerKey $ConsumerSecret

# Define time range and product details
PRODUCT="EO:EUM:DAT:MSG:HRSEVIRI" # standard msg files (15 mins res)
#PRODUCT="EO:EUM:DAT:MSG:MSG15-RSS" # high rate scans
FORMAT='msgnative' # 'hrit','netcdf4'
#ROI=[52, 42, 5, 16] #NSWE --> expats

# Number of files to process at a time
batch_size=10

# Define logfile
LOG_FILE=${DOWNLOAD_DIR}"logfile.txt"

# Path to the Python script
python_script_path="download/check_file_presence.py"

#remove entire order history
eumdac order delete --all

#clean all old customization to free up memory
eumdac tailor clean --all


# Create a list of products to download
#eumdac search -c $PRODUCT --start $START_TIME --end $END_TIME --bbox 5 48 9 52 --limit 3 > products.txt
eumdac search -c $PRODUCT --start $START_TIME --end $END_TIME  > /net/ostro/msg_download_info_files/products.txt
#The search and browse APIs are limited to return a maximum of 10.000 items.
#if you first do the order and then download it seems not able to perfrom multiple file at time (only using download directy)
#check customization using yaml files
#When using a bounding box geometry for filter products, the values needs to be in WSEN order(west, south, east, north).

# Print the number of lines before checking
echo "Number of lines before checking: $(wc -l < /net/ostro/msg_download_info_files/products.txt)"

# Temporary file to store products that don't exist
touch /net/ostro/msg_download_info_files/temp_products.txt

# Read each line in products.txt
while IFS= read -r line; do
    # Call the Python script with each filename, download directory, and format
    result=$(python3 "$python_script_path" "$line" "$DOWNLOAD_DIR" "$FORMAT")
    echo "$result"
    
    # check using grep
    if echo "$result" | grep -q "does not exist"; then
        echo "$line" >> /net/ostro/msg_download_info_files/temp_products.txt
    fi
done < "/net/ostro/msg_download_info_files/products.txt"

# Replace the original products.txt with the temp file containing only products that don't exist
mv "/net/ostro/msg_download_info_files/temp_products.txt" "/net/ostro/msg_download_info_files/products.txt"

# Print the number of lines after checking
echo "Number of lines after checking: $(wc -l < /net/ostro/msg_download_info_files/products.txt)"

# Check if the file exists and has a size greater than zero
if [ -s "/net/ostro/msg_download_info_files/products.txt" ]; then
    # File exists and has content, continue with the rest of the script
    echo "Files are available for download."

    # Count the total number of lines/files in products.txt
    total_lines=$(wc -l < /net/ostro/msg_download_info_files/products.txt)

    # Calculate the number of batches needed
    num_batches=$(( (total_lines + batch_size - 1) / batch_size ))

    # Temporary file to store products that don't exist
    touch /net/ostro/msg_download_info_files/temp_batch_files.txt

    # Loop through each batch
    for (( batch=1; batch<=num_batches; batch++ ))
    do
        # Calculate line numbers for the current batch
        start_line=$(( (batch - 1) * batch_size + 1 ))
        end_line=$(( batch * batch_size ))

        # Extract the current batch of lines from products.txt and store in a temporary file
        sed -n "${start_line},${end_line}p" /net/ostro/msg_download_info_files/products.txt > /net/ostro/msg_download_info_files/temp_batch_files.txt

        # Process each file in the current batch
        echo "Processing batch $batch:"
        
        # Download the products without saving output to a log file
        eumdac download -c $PRODUCT -p @temp_batch_files.txt --tailor 'product: HRSEVIRI, format: '$FORMAT', roi: {'NSWE':[52, 42, 5, 16]}' -o $DOWNLOAD_DIR -y

        #eumdac download -c $PRODUCT -p @temp_batch_files.txt --tailor 'product: HRSEVIRI, format: '$FORMAT', compression: zip' -o $DOWNLOAD_DIR -y 
        #eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --tailor 'product: HRSEVIRI, format: '$FORMAT', roi: {'NSWE':[52, 42, 5, 16]}' -o $DOWNLOAD_DIR -y
        #eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --tailor 'product: HRSEVIRI, projection: geographic, format: netcdf4, roi: {'NSWE': [52, 48, 5, 9]}' -o $DOWNLOAD_DIR 
        #eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --bbox 5 48 9 52 -o $DOWNLOAD_DIR 
        #bbox only select the data containing that area? crop should be done inside --tailor? or the problem was only this polar orbit satellite? check

        # Find and unzip .nat files in the same directory (use only with nat format)
        # find "$DOWNLOAD_DIR" -name '*.zip' -exec sh -c 'unzip -j "$1" "*.nat" -d "$2"' sh {} "$DOWNLOAD_DIR" \;

        #delete the customization

        #remove entire order history, maybe not needed!
        eumdac order delete --all

        #clean all old customization to free up memory, maybe not needed!
        eumdac tailor clean --all
    done

    # Clean up the temporary file after all batches are processed
    rm /net/ostro/msg_download_info_files/temp_batch_files.txt

else
    # File is empty or does not exist, print message and exit
    echo "No files are available to download."

fi


# End time
script_end_time=$(date +%s)

# Compute and print the elapsed time
elapsed_time=$((script_end_time - script_start_time))

# Print the elapsed time to the log file
echo "Elapsed Time: $elapsed_time seconds" >> "$LOG_FILE"

echo "Download concluded!"



