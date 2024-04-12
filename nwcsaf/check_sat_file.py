"""
This script is designed to count and record specific satellite data files present within a given directory,
identifying dates on which all expected data files (assuming 90 per date) are available. The results are 
recorded in an output text file.

Key functionalities include:
- Traversing a specified directory to enumerate files that match a certain naming pattern indicative of satellite data.
- Counting files per date using a filename component that is assumed to represent the date of the data.
- Writing the dates with a complete set of data (90 files) to an output file.

Parameters:
- `directory`: The path to the directory where satellite data files are located.
- `output_file`: The path to the output file where dates with complete data sets are recorded.

Assumptions:
- Filenames are formatted with parts separated by '-', where one part represents the date.
- Each date should ideally have 90 files to be considered complete.

The script prints the location of the output file upon successful completion of data recording.
"""

import os
from collections import defaultdict

# Specify the directory to check
directory = '/work/NWC_GEO/import/Sat_data'
output_file = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/hrit_avail_list_paula.txt'

# A dictionary to hold counts of files for each timestamp-channel combination
file_counts = defaultdict(int)


# List all files in the specified directory
for filename in os.listdir(directory):
    # Assuming the date is always at a specific position in the filename
    # Adjust the slicing according to your filename format
    if filename.startswith('H-000-MSG'):
        date = filename.split('-')[-2]  # Extracting date part 
        file_counts[date] += 1

# Open the output file for writing
with open(output_file, 'w') as f:
    # Iterate over dates in sorted order
    for date in sorted(file_counts):
        if file_counts[date] == 90:
            f.write(f"{date}\n")

print(f"Output written to {output_file}")

