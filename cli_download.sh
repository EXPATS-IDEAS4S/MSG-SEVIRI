#!/bin/bash

# Start time
start_time=$(date +%s)

# Set your credentials (find them in EUMETSAT profile portal)
ConsumerKey='MwVGCDXIMtsN7Cj28dGBz4UcZYga'
ConsumerSecret='Lepxj10Ag3p2R5FVdpwvP08Ny_Ia'
eumdac set-credentials $ConsumerKey $ConsumerSecret

# Define time range and product details
PRODUCT="EO:EUM:DAT:MSG:HRSEVIRI"
START_TIME="2021-07-14T12:00"
END_TIME="2021-07-14T15:00"

# Define the directory where to save the downloaded data
DOWNLOAD_DIR="/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_FullDisk/"
LOG_FILE="/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_FullDisk/logfile.txt"

# Create a list of products to download
eumdac search -c $PRODUCT --start $START_TIME --end $END_TIME > products.txt

# Download the products without saving output to a log file
eumdac download -c $PRODUCT -p @products.txt -o $DOWNLOAD_DIR --limit 3

# Find and unzip .nat files in the same directory
find "$DOWNLOAD_DIR" -name '*.zip' -exec sh -c 'unzip -j "$1" "*.nat" -d "$2"' sh {} "$DOWNLOAD_DIR" \;

# End time
end_time=$(date +%s)

# Compute and print the elapsed time
elapsed_time=$((end_time - start_time))

# Print the elapsed time to the log file
echo "Elapsed Time: $elapsed_time seconds" >> "$LOG_FILE"