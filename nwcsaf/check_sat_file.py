import os
from collections import defaultdict

# Specify the directory to check
directory = '/work/dcorradi/NWC_GEO/import/Sat_data'
output_file = '/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/hrit_avail_list.txt'

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

