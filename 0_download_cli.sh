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
DOWNLOAD_DIR="/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220714_20210715_Flood_domain_DataTailor_CLI_nc/"
LOG_FILE="/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220714_20210715_Flood_domain_DataTailor_CLI_nc/logfile.txt"

# Create a list of products to download
#eumdac search -c $PRODUCT --start $START_TIME --end $END_TIME --bbox 5 48 9 52 --limit 3 > products.txt
#if you first do the order and then download it seems not able to perfrom multiple file at time (only using download directy)
#check customization using yaml files

#When using a bounding box geometry for filter products, the values needs to be in WSEN order(west, south, east, north).
#$ eumdac download -c EO:EUM:DAT:METOP:ASCSZR1B --bbox -180 -90 180 90 
#lonmin, latmin, lonmax, latmax= 5, 48, 9, 52

#eumdac order delete 2024-01-24#0001

# Download the products without saving output to a log file
#eumdac download -c $PRODUCT -p @products.txt -o $DOWNLOAD_DIR  
#eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --tailor 'product: HRSEVIRI, format: msgnative, roi: {'NSWE': [52, 48, 5, 9]}' -o $DOWNLOAD_DIR

eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --tailor 'product: HRSEVIRI, projection: geographic, format: netcdf4, roi: {'NSWE': [52, 48, 5, 9]}' -o $DOWNLOAD_DIR 

#eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --bbox 5 48 9 52 -o $DOWNLOAD_DIR 
#bbox only select the data containing that area? crop should be done inside --tailor? or the problem was only this polar orbit satellite? check

# Find and unzip .nat files in the same directory
# find "$DOWNLOAD_DIR" -name '*.zip' -exec sh -c 'unzip -j "$1" "*.nat" -d "$2"' sh {} "$DOWNLOAD_DIR" \;

# End time
end_time=$(date +%s)

# Compute and print the elapsed time
elapsed_time=$((end_time - start_time))

# Print the elapsed time to the log file
echo "Elapsed Time: $elapsed_time seconds" >> "$LOG_FILE"
