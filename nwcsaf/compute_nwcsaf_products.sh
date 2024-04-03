#!/bin/bash

# Define scripts
PYTHON_SCRIPT="/home/dcorradi/Documents/Codes/MSG-SEVIRI/download/find_missing_timestamps.py"
DOWNLOAD_SCRIPT="/home/dcorradi/Documents/Codes/MSG-SEVIRI/download/download_cli.sh"
UNZIP_SCRIPT="/home/dcorradi/Documents/Codes/MSG-SEVIRI/download/unzip_files.sh"
NWC_SAF_COMMAND="SAFNWCTM"
CLEANUP_SCRIPT="./cleanup_script.sh"  # If you have a specific cleanup operation

#Define Folders
DOWNLOAD_FOLDER="/work/NWC_GEO/import/Sat_data/"
UNZIPPED_FOLDER="/work/NWC_GEO/import/Sat_data/"
NWC_SAF_OUTPUT_FOLDER="/work/NWC_GEO/"
CODE_FOLDER="/home/dcorradi/Documents/Codes/MSG-SEVIRI/nwcsaf/"

#Define other parameters
BATCH_SIZE=100  # Number of files per batch, 
START_DATE="2023-07-01"
END_DATE="2023-07-31"
MISSING_TIMESTAMPS_FILE="missing_timestamps.txt"

# Generate a list of missing timestamps and save to file
python $PYTHON_SCRIPT "$START_DATE" "$END_DATE" "$UNZIPPED_FOLDER" > $MISSING_TIMESTAMPS_FILE

# Read missing timestamps into an array
mapfile -t MISSING_TIMESTAMPS_ARRAY < $MISSING_TIMESTAMPS_FILE

# Check for no missing timestamps
if [ ${#MISSING_TIMESTAMPS_ARRAY[@]} -eq 0 ]; then
    echo "No missing timestamps detected. All data is present."
    exit 0
fi

echo "Processing ${#MISSING_TIMESTAMPS_ARRAY[@]} missing timestamps in batches..."

# Processing batches of missing timestamps
for (( i=0; i<${#MISSING_TIMESTAMPS_ARRAY[@]}; i+=BATCH_SIZE )); do
    BATCH_TIMESTAMPS=("${MISSING_TIMESTAMPS_ARRAY[@]:i:BATCH_SIZE}")
    echo "Processing batch: ${BATCH_TIMESTAMPS[*]}"
    
    # Convert batch timestamps to a space-separated string
    batch_timestamps_str="${BATCH_TIMESTAMPS[*]}"

    # Call the Python script and read the output into variables
    read start_time end_time <<< $(python extract_dates.py $batch_timestamps_str)

    # Now, you can use $start_time and $end_time with your download script
    echo "START_TIME=$start_time, END_TIME=$end_time"

    # Adjust the call to your download script to use $start_time and $end_time
    if ! $DOWNLOAD_SCRIPT "$start_time" "$end_time" "$DOWNLOAD_FOLDER"; then
        echo "Error during download for timestamps: ${BATCH_TIMESTAMPS[*]}"
        continue  # Proceed to the next batch
    fi

    # Unzip the downloaded files
    if ! $UNZIP_SCRIPT $DOWNLOAD_FOLDER $UNZIPPED_FOLDER; then
        echo "Error unzipping files for timestamps: ${BATCH_TIMESTAMPS[*]}"
        # Decide whether to continue or stop; for now, we'll continue to the next batch
    fi

    # Process the data from the specific folder
    (
    cd "$UNZIPPED_FOLDER" && SAFNWCTM
    if [ $? -ne 0 ]; then
        echo "Error processing files for timestamps: ${BATCH_TIMESTAMPS[*]}"
        # Continue to the next batch
    fi
    )

    #check if the NWCSAF process is over -->use the logfile last row


    # Optional: Cleanup after processing
    if [[ -f "$CLEANUP_SCRIPT" ]]; then
        $CLEANUP_SCRIPT $UNZIPPED_FOLDER
    fi

    echo "Batch processed. Moving to the next batch..."
done

echo "All data processing completed."