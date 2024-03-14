#!/bin/bash

# Define configurations
DOWNLOAD_SCRIPT="/home/dcorradi/Documents/Codes/MSG-SEVIRI/download/download_cli.sh"
UNZIP_SCRIPT="/home/dcorradi/Documents/Codes/MSG-SEVIRI/download/unzip_files.sh"
DOWNLOAD_FOLDER="/work/NWC_GEO/import/Sat_data/"
UNZIPPED_FOLDER="/work/NWC_GEO/import/Sat_data/"
NWC_SAF_OUTPUT_FOLDER="/work/NWC_GEO/"
NWC_SAF_COMMAND="SAFNWCTM"

BATCH_SIZE=100  # Number of files per batch, 

PYTHON_SCRIPT="/home/dcorradi/Documents/Codes/MSG-SEVIRI/download/find_missing_timestamps.py"
START_DATE="2024-01-01"
END_DATE="2024-01-31"

PROCESSING_SCRIPT="./processing_script.sh"
CLEANUP_SCRIPT="./cleanup_script.sh"  # If you have a specific cleanup operation


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
    
    # Download data for the current batch of timestamps
    if ! $DOWNLOAD_SCRIPT "${BATCH_TIMESTAMPS[@]}"; then
        echo "Error during download for timestamps: ${BATCH_TIMESTAMPS[*]}"
        continue  # Proceed to the next batch
    fi

    # Unzip the downloaded files
    if ! $UNZIP_SCRIPT $DOWNLOAD_FOLDER $UNZIPPED_FOLDER; then
        echo "Error unzipping files for timestamps: ${BATCH_TIMESTAMPS[*]}"
        # Decide whether to continue or stop; for now, we'll continue to the next batch
    fi

    # Process the data
    if ! $PROCESSING_SCRIPT $UNZIPPED_FOLDER; then
        echo "Error processing files for timestamps: ${BATCH_TIMESTAMPS[*]}"
        # Continue to the next batch
    fi

    # Optional: Cleanup after processing
    if [[ -f "$CLEANUP_SCRIPT" ]]; then
        $CLEANUP_SCRIPT $UNZIPPED_FOLDER
    fi

    echo "Batch processed. Moving to the next batch..."
done

echo "All data processing completed."