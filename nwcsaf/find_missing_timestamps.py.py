import os
import sys
from datetime import datetime, timedelta
from collections import defaultdict

def generate_timestamps(start_date, end_date):
    delta = timedelta(minutes=15)
    current = start_date
    while current <= end_date:
        yield current
        current += delta

def list_missing_timestamps(start_date, end_date, directory, expected_files_per_interval=90):
    # Generate all 15-minute timestamps between start_date and end_date
    all_timestamps = list(generate_timestamps(start_date, end_date))

    # Count files for each timestamp
    file_counts = defaultdict(int)
    for f in os.listdir(directory):
        # Parse timestamp from filename
        try:
            timestamp = datetime.strptime(f.split('-')[-2], '%Y%m%d%H%M')
            file_counts[timestamp] += 1
        except (ValueError, IndexError):
            continue  # Skip files that do not match the expected format or parsing fails

    # Identify missing timestamps
    missing_timestamps = [ts for ts in all_timestamps if file_counts[ts] < expected_files_per_interval]

    return missing_timestamps

if __name__ == "__main__":
    start_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')
    end_date = datetime.strptime(sys.argv[2], '%Y-%m-%d')
    directory = sys.argv[3]
    missing_timestamps = list_missing_timestamps(start_date, end_date, directory)
    # Open the output file for writing
    output_file = directory+"missing_files.txt"
    with open(output_file, 'w') as f:
        for timestamp in missing_timestamps:
            print(timestamp.strftime('%Y%m%d%H%M'))
            f.write(timestamp.strftime('%Y%m%d%H%M')+"\n")            

    print(f"Output written to {output_file}")



