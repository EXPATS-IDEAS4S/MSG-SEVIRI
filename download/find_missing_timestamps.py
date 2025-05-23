"""
This script checks for missing files based on their timestamps within a specified directory,
rounding the timestamps to the nearest 15-minute interval. 
The script identifies any expected timestamps (rounded to the nearest 15 minutes) 
that do not have corresponding files within the given date range.

Usage:
    python check_missing_files.py
    (Optionally, parameters can be provided through the command line as shown below.)
    python check_missing_files.py <start_date> <end_date> 

Default Parameters (if not provided):
    <start_date>  - 'YYYY-MM-DD' (e.g., '2023-01-01')
    <end_date>    - 'YYYY-MM-DD' (e.g., '2023-01-31')
    directory   - Path to the directory containing the files to be checked.
    log_dir    - path to directory to save the list of missing time stamps
    format     - type of the file format, e.g msgnative, hrit, netcdf4

Output:
    A text file named 'missing_timestamps.txt' within the specified directory, listing
    all missing timestamps (rounded to the nearest 15 minutes) within the specified date range.
"""
# %%
import os
import sys
import glob
from datetime import datetime, timedelta
from collections import defaultdict

# get path of this file
dir_path = os.path.dirname(os.path.abspath(__file__))

# Default parameters
DEFAULT_START_DATE = '2021-06-01'
DEFAULT_END_DATE = '2021-07-01'
directory = '/data/sat/msg/rapid_scan/nat/2021/06/'
msg_res = 5
log_dir = os.path.join(dir_path, 'log')
format = 'msgnative' 

def generate_timestamps(start_date, end_date, msg_res=15):
    """Generates all 15-minute intervals between start_date and end_date."""
    delta = timedelta(minutes=msg_res)
    current = start_date
    while current < end_date:
        yield current
        current += delta

def round_down_to_msg_timestamp(dt, msg_res=15):
    """
    Rounds down a datetime object to the nearest 5-minute interval.
    
    Parameters:
        dt (datetime): The datetime object to round down.
        msg_res (int): The resolution in minutes to round down to. Default is 15 minutes.
    
    Returns:
        datetime: The rounded-down datetime object.
    """
    # Calculate the number of minutes to subtract to reach the nearest 5-minute interval
    minutes_to_subtract = dt.minute % msg_res
    rounded_time = dt - timedelta(minutes=minutes_to_subtract, 
                                  seconds=dt.second, 
                                  microseconds=dt.microsecond)
    return rounded_time


def find_date_string(filename, file_format):
    """
    Extracts and adjusts the date string from filenames based on the specified file format.
    hrit filenames: H-000-MSG4__-MSG4________-WV_073___-000003___-202107141200-__
    nat filenames example: MSG3-SEVI-MSG15-0100-NA-20230731215741.559000000Z-NA.subset.nat
    nc filename example: HRSEVIRI_20210715T101510Z_20210715T102742Z_epct_34b8524d_PC.nc
    
    Parameters:
        filename (str): The name of the file from which to extract the date string.
        file_format (str): The format of the file, which affects how the date string is extracted.
    
    Returns:
        str: The adjusted date string in Format YYYYMMDDHHMM.
    """
    # For 'hrit' or 'hrit_compressed' formats
    if file_format in ['hrit', 'hrit_compressed']:
        time_str = filename.split('-')[-2]  # Assumes the date string is in the second to last segment
        return time_str # Format YYYYMMDDHHMM

    # For 'msgnative' format
    elif file_format == 'msgnative':
        parts = filename.split('.')[0].split('-')[-1]
        return parts[:12] # Format YYYYMMDDHHMM  
    
    # For 'netcdf4' format
    elif file_format == 'netcdf4':
        parts = filename.split('.')[0].split('_')
        date_str = parts[1]  # Assumes the date string follows the first underscore
        return date_str[:8] + date_str[9:11] + date_str[12:14]  # Format YYYYMMDDHHMM
    
    else:
        print("Format not recognized.")
        return None
    

def get_all_files_in_directory(directory, file_format):
    """
    """
    #TODO: add for extension of other formats
    # For 'msgnative' format
    if file_format == 'msgnative':
        return sorted(glob.glob(f'{directory}/**/*.nat', recursive=True))
    

def list_missing_timestamps(start_date, end_date, directory, msg_res, format, expected_files_per_interval=1):
    # Generate all 15-minute timestamps between start_date and end_date
    all_timestamps = list(generate_timestamps(start_date, end_date, msg_res=msg_res))
    #print(all_timestamps)

    # read in all filenames in directory (and subdirectories)
    files = get_all_files_in_directory(directory, format)

    # Count files for each timestamp
    file_counts = defaultdict(int)
    for f in files:
        # Parse timestamp from filename
        try:
            datestring = find_date_string(f,format)
            timestamp = datetime.strptime(datestring, '%Y%m%d%H%M')
            timestamp = round_down_to_msg_timestamp(timestamp, msg_res=msg_res)
            file_counts[timestamp] += 1
            #print(timestamp)
        except (ValueError, IndexError):
            continue  # Skip files that do not match the expected format or parsing fails

    # Identify missing timestamps
    missing_timestamps = [ts for ts in all_timestamps if file_counts[ts] < expected_files_per_interval]

    return missing_timestamps


# %%
if __name__ == "__main__":
    start_date = datetime.strptime(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_START_DATE, '%Y-%m-%d')
    end_date = datetime.strptime(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_END_DATE, '%Y-%m-%d')

    missing_timestamps = list_missing_timestamps(start_date, end_date, directory, msg_res, format)
    output_file = os.path.join(log_dir, "missing_timestamps.txt")
    
    with open(output_file, 'w') as f:
        f.write(f"{len(missing_timestamps)} missing timestamps found between {start_date} and {end_date}:\n")
        for ts in missing_timestamps:
            f.write(ts.strftime('%Y-%m-%d %H:%M:%S') + "\n")
    
    print(f"{len(missing_timestamps)} missing timestamps written to {output_file}")




# %%
