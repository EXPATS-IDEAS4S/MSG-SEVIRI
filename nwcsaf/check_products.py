import glob
import os
from datetime import datetime

# Define the directory to search for files
directory = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI'
# Define the file pattern to match
file_pattern = 'S_NWC_CI_MSG3_EXPATS-VISIR_*.nc'
# Define the output text file where timestamps will be saved
output_file = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/file_timestamps.txt'

# Construct the full pattern
full_pattern = os.path.join(directory, file_pattern)

# Search for files matching the pattern
files = sorted(glob.glob(full_pattern))

# Extract timestamps from filenames
timestamps = []
for file in files:
    # Extract the filename from the path
    filename = os.path.basename(file)
    # Assume the timestamp is after the last dash '-' and before the first dot '.'
    timestamp_str = filename.split('.')[0].split('_')[-1]
    try:
        # Convert the string to a datetime object (modify the format as per your filenames)
        timestamp = datetime.strptime(timestamp_str, '%Y%m%dT%H%M%SZ')
        timestamps.append(timestamp)
    except ValueError as e:
        print(f"Could not parse timestamp from {filename}: {e}")

# Save the timestamps to the output file
with open(output_file, 'w') as f:
    for timestamp in timestamps:
        # Write each timestamp in a human-readable format
        f.write(timestamp.strftime('%Y%m%d%H%M') + '\n')
        #f.write(timestamp + '\n')

print(f"Timestamps saved to {output_file}")
