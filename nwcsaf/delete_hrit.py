"""
This script processes a list of timestamps, searches for files matching those timestamps in a specified
directory, and deletes those files. It records the paths of the deleted files in a separate output file.

The script executes the following operations:
- Reads a list of timestamps from a specified text file.
- Constructs file search patterns based on these timestamps.
- Searches for and identifies files matching the constructed patterns in a target directory.
- Writes the paths of the files identified for deletion to an output file.
- Deletes the identified files and logs the deletion or any errors encountered during the process.

Usage:
- The script assumes timestamps are provided in a specific format in the text file.
- Ensure the file pattern in the target folder includes a placeholder for the timestamp which this script replaces dynamically.

Parameters:
- `timestamps_file`: Path to the text file containing timestamps.
- `target_folder`: Directory where files to be deleted are located.
- `file_pattern`: Pattern of the files to search for, with a placeholder for the timestamp.
- `output_file`: Path to the file where the paths of the deleted files are recorded.

Assumptions:
- Timestamps are assumed to be in the format 'YYYY-mm-dd HH:MM:SS' in the timestamps file.
- Filenames in the target folder contain these timestamps in a different format, 'YYYYmmddTHHMMSSZ',
  which requires conversion of the timestamps before file matching.

Note:
- The deletion process is irreversible. Make sure to have backups or a verification step if necessary.

Output:
- For each file deleted, the script logs the path in an output file and prints a message to the console.
- After completion, a final message indicating the end of the operation is printed.

Errors:
- The script handles `OSError` during file deletion and logs any issues encountered.
"""

import os
import glob

# Define the path to the text file containing the timestamps
timestamps_file = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/file_timestamps.txt'
# Define the target folder where files will be searched and deleted
target_folder = '/net/morget/dcorradi/NWCGEO/import/Sat_data'
# Define the pattern of the files in the target folder, assuming timestamp is part of the filename
file_pattern = 'H-000-MSG*__-MSG*________-*___-*___-@-__' #H-000-MSG3__-MSG3________-WV_073___-000008___-202307152345-__
#path for storing deleted hrit files
output_file = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/hrit_del_list.txt'

# Read the timestamps from the text file
with open(timestamps_file, 'r') as f:
    timestamps = [line.strip() for line in f.readlines()]

# Convert timestamps to the format used in filenames (if necessary)
# This step assumes the timestamps in the text file are in the 'YYYY-mm-dd HH:MM:SS' format
# and need to be converted to 'YYYYmmddTHHMMSSZ' to match the filename pattern.
#timestamps_in_filename_format = [ts.replace('-', '').replace(':', '').replace(' ', 'T') + 'Z' for ts in timestamps]

# Search and delete files with matching timestamps
for ts in timestamps:
    # Construct the glob pattern for each timestamp
    specific_pattern = file_pattern.replace('@', ts)
    # Find all files that match this specific timestamp pattern
    files_to_delete = glob.glob(os.path.join(target_folder, specific_pattern))

    # Save the timestamps to the output file
    with open(output_file, 'a') as f:
        # Write each timestamp in a human-readable format
        for item in files_to_delete:
            f.write(item + '\n')

    print(f"Timestamps saved to {output_file}")
    
    # Delete the files
    for file_path in files_to_delete:
        try:
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        except OSError as e:
            print(f"Error deleting {file_path}: {e}")

print("Operation completed.")
