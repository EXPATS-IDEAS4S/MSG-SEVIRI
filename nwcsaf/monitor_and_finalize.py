import time
import subprocess
import shutil
import os
import re
from datetime import datetime

def monitor_log_file(log_file_path, default_end_time=None):
    """
    Monitors the last line of a log file for a completion message containing an end time.

    Parameters:
    - log_file_path: Path to the log file.
    - default_end_time: Default end time to use if not found in the log (optional).
    
    Returns:
    - The detected or default end time.
    """
    completion_pattern = r"All PGEs for Slot (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) have concluded."
    
    while True:
        try:
            with open(log_file_path, 'r') as log_file:
                for last_line in log_file:
                    pass
            match = re.search(completion_pattern, last_line)
            if match:
                end_time = match.group(1)
                print(f"Process completed at {end_time}.")
                return end_time
        except FileNotFoundError:
            print(f"Log file not found: {log_file_path}")
            break

        time.sleep(10)  # Check every 10 seconds
    
    if default_end_time:
        print(f"Using default end time: {default_end_time}")
        return default_end_time
    else:
        return None

def quit_process_and_move_files(src_dir, dest_dir):
    """
    Quits the process and moves files from src_dir to dest_dir.

    Parameters:
    - src_dir: Source directory of the files to move.
    - dest_dir: Destination directory where files should be moved.
    """
    # Quit the process
    subprocess.run(['tm', 'quit'], check=True)
    
    # Move the files
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    for filename in os.listdir(src_dir):
        shutil.move(os.path.join(src_dir, filename), dest_dir)

if __name__ == "__main__":
    log_file_path = '/path/to/your/logfile.log'
    default_end_time = "2023-07-12T00:00:00Z"  # Set your default end time here if needed
    src_dir = '/path/to/source/directory'
    dest_dir = '/path/to/destination/directory'

    end_time = monitor_log_file(log_file_path, default_end_time)
    if end_time:
        quit_process_and_move_files(src_dir, dest_dir)
    else:
        print("Process monitoring was not completed successfully.")
