"""
This script processes IR crop files and cloud physical properties files to combine their data based on matching timestamps.

The script consists of the following main components:
1. Function `find_corresponding_file`: Finds the corresponding cloud file based on the timestamp.
2. Function `process_files`: Processes IR and cloud physical properties files to combine the data.
3. Main execution block: Defines directories, retrieves lists of files, and processes them.

Example Usage:
--------------
1. Define the directory paths for crop files, cloud files, and output files.
2. Ensure the directories and NetCDF files are correctly specified.
3. Run the script to combine the IR crop files with the corresponding cloud physical properties data based on timestamps.
"""

import xarray as xr
import os
from glob import glob

def find_corresponding_file(cloud_list, target_time):
    """
    Find the corresponding cloud file based on the timestamp.

    Parameters:
    -----------
    cloud_list : list of str
        List of file paths to the cloud properties NetCDF files.
    target_time : numpy.datetime64
        The timestamp for which the corresponding cloud file is needed.

    Returns:
    --------
    str or None
        The file path of the corresponding cloud file if found, otherwise None.
    """
    for filename in cloud_list:
        ds = xr.open_dataset(filename, decode_times=True)
        if 'time' in ds.coords and target_time in ds['time'].values:
            return filename
    return None

def process_files(crops_list, cloud_list, output_dir):
    """
    Process IR and cloud physical properties files to combine the data.

    Parameters:
    -----------
    crops_list : list of str
        List of file paths to the crop (IR) NetCDF files.
    cloud_list : list of str
        List of file paths to the cloud properties NetCDF files.
    output_dir : str
        Directory where the combined output files will be saved.

    Returns:
    --------
    None
    """
    for crop_file in crops_list:
        crop_ds = xr.open_dataset(crop_file, decode_times=True)
        #print(crop_ds)

        # Get the time from the IR file
        crop_time = crop_ds['time'].values[0]
        print(crop_time)

        # Find the corresponding cloud file based on the time
        cloud_filepath = find_corresponding_file(cloud_list, crop_time)
        if cloud_filepath is None:
            print(f"No matching cloud file found for time: {crop_time}")
            continue

        cloud_ds = xr.open_dataset(cloud_filepath, decode_times=True)
        #print(cloud_ds)

        # Select the data within the lat/lon bounds of the IR data
        lat_bounds = crop_ds['lat'].values[[0, -1]]
        lon_bounds = crop_ds['lon'].values[[0, -1]]
        #print(lat_bounds, lon_bounds)

        cloud_ds_sel = cloud_ds.sel(
            lat=slice(lat_bounds[0], lat_bounds[1]),
            lon=slice(lon_bounds[0], lon_bounds[1]),
            time=crop_time
        )

        #output_filename = crop_file
        output_filepath = output_dir+crop_file.split('/')[-1]
        #print(output_filepath)

        # Save the combined dataset to a new NetCDF file
        cloud_ds_sel.to_netcdf(output_filepath)
        print(f"Saved combined dataset to {output_filepath}")

# Define directories
crop_directory = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc/'
cloud_directory = '/data/sat/msg/CM_SAF/merged_cloud_properties/2013/'
output_directory = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc_clouds/'

# Check if the directory exists
if not os.path.exists(output_directory):
    # Create the directory if it doesn't exist
    os.makedirs(output_directory) 

#get list of cloud properties files and crop files
crops_list = sorted(glob(f'{crop_directory}*.nc'))
#print(crops_list)
clouds_list = sorted(glob(f'{cloud_directory}*/*.nc'))
#print(clouds_list)


# Process the files
process_files(crops_list, clouds_list, output_directory)

