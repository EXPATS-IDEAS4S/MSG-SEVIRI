#!/bin/bash

# Start time
start_time=$(date +%s)

# Execute the Python script to get credentials
credentials=$(python credentials.py)

# Use an array to split the credentials output
readarray -td' ' cred_array <<<"$credentials"; declare -p cred_array

ConsumerKey=${cred_array[0]}
ConsumerSecret=${cred_array[1]}

# Trim possible trailing newline
ConsumerKey=$(echo $ConsumerKey | tr -d '\n')
ConsumerSecret=$(echo $ConsumerSecret | tr -d '\n')

eumdac set-credentials $ConsumerKey $ConsumerSecret

# Define time range and product details
PRODUCT="EO:EUM:DAT:MSG:HRSEVIRI"
START_TIME="2021-07-12T00:00"
END_TIME="2021-07-16T00:00"
FORMAT='hrit' #'msgnative','netcdf4',
#ROI=[52, 48, 5, 9] #NSWE

# Number of files to process at a time
batch_size=10

# Define the directory where to save the downloaded data
DOWNLOAD_DIR='/work/NWC_GEO/import/Sat_data/'
LOG_FILE=${DOWNLOAD_DIR}"logfile.txt"
# Path to the Python script
python_script_path="/home/dcorradi/Documents/Codes/MSG-SEVIRI/readers/check_file_precence.py"

#remove entire order history
eumdac order delete --all

#clean all old customization to free up memory
eumdac tailor clean --all

# Create a list of products to download
#eumdac search -c $PRODUCT --start $START_TIME --end $END_TIME --bbox 5 48 9 52 --limit 3 > products.txt
eumdac search -c $PRODUCT --start $START_TIME --end $END_TIME  > products.txt
#The search and browse APIs are limited to return a maximum of 10.000 items.
#if you first do the order and then download it seems not able to perfrom multiple file at time (only using download directy)
#check customization using yaml files
#When using a bounding box geometry for filter products, the values needs to be in WSEN order(west, south, east, north).

# Print the number of lines before checking
echo "Number of lines before checking: $(wc -l < products.txt)"

# Temporary file to store products that don't exist
touch temp_products.txt

# Read each line in products.txt
while IFS= read -r line; do
    # Call the Python script with each filename, download directory, and format
    result=$(python "$python_script_path" "$line" "$DOWNLOAD_DIR" "$FORMAT")
    echo "$result"
    
    # check using grep
    if echo "$result" | grep -q "does not exist"; then
        echo "$line" >> temp_products.txt
    fi
done < "products.txt"

# Replace the original products.txt with the temp file containing only products that don't exist
mv "temp_products.txt" "products.txt"

#remove temp file
rm temp_products.txt

# Print the number of lines after checking
echo "Number of lines after checking: $(wc -l < products.txt)"

# Check if the file exists and has a size greater than zero
if [ -s "products.txt" ]; then
    # File exists and has content, continue with the rest of the script
    echo "Files are available for download."

    # Count the total number of lines/files in products.txt
    total_lines=$(wc -l <products.txt)

    # Calculate the number of batches needed
    num_batches=$(( (total_lines + batch_size - 1) / batch_size ))

    # Temporary file to store products that don't exist
    touch temp_batch_files.txt

    # Loop through each batch
    for (( batch=1; batch<=num_batches; batch++ ))
    do
        # Calculate line numbers for the current batch
        start_line=$(( (batch - 1) * batch_size + 1 ))
        end_line=$(( batch * batch_size ))

        # Extract the current batch of lines from products.txt and store in a temporary file
        sed -n "${start_line},${end_line}p" products.txt > temp_batch_files.txt

        # Process each file in the current batch
        echo "Processing batch $batch:"
        
        # Download the products without saving output to a log file
        eumdac download -c $PRODUCT -p @temp_batch_files.txt --tailor 'product: HRSEVIRI, format: '$FORMAT', compression: zip' -o $DOWNLOAD_DIR -y 
        #eumdac download -c $PRODUCT --start $START_TIME --end $END_TIME --tailor 'product: HRSEVIRI, format: msgnative, roi: {'NSWE': [52, 48, 5, 9]}' -o $DOWNLOAD_DIR
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
    rm temp_batch_files.txt

else
    # File is empty or does not exist, print message and exit
    echo "No files are available to download."

fi


# End time
end_time=$(date +%s)

# Compute and print the elapsed time
elapsed_time=$((end_time - start_time))

# Print the elapsed time to the log file
echo "Elapsed Time: $elapsed_time seconds" >> "$LOG_FILE"

exit 1

