import os
import glob

# Define the path to the text file containing the timestamps
timestamps_file = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/file_timestamps.txt'
# Define the target folder where files will be searched and deleted
target_folder = '/work/NWC_GEO/import/Sat_data'
# Define the pattern of the files in the target folder, assuming timestamp is part of the filename
file_pattern = 'H-000-MSG3__-MSG3________-*___-*___-@-__' #H-000-MSG3__-MSG3________-WV_073___-000008___-202307152345-__
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
