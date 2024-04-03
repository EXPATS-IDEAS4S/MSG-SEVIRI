import sys
from datetime import datetime

# Function to convert timestamp list to start and end dates
def get_start_end_dates(timestamps):
    # Convert string timestamps to datetime objects
    dates = [datetime.strptime(ts, "%Y%m%d%H%M") for ts in timestamps]
    
    # Find start (earliest) and end (latest) dates
    start_date = min(dates)
    end_date = max(dates)
    
    # Format dates back to strings
    start_time_str = start_date.strftime("%Y-%m-%dT%H:%M")
    end_time_str = end_date.strftime("%Y-%m-%dT%H:%M")
    
    return start_time_str, end_time_str

# Read timestamps from command line arguments
timestamps = sys.argv[1:]

# Calculate start and end dates
start_time, end_time = get_start_end_dates(timestamps)

# Print the results
print(start_time)
print(end_time)
