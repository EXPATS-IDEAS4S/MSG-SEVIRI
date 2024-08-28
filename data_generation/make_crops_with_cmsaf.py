"""
This script processes IR crop files and cloud physical properties files to create nc crops of CMA that matches the one with IR.

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
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor

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



def process_files_old(crops_list, cloud_list, output_dir):
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

        #TODO try to include the same amount of pixels, maybe slice not proper or regrid didn't work?
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

def convert_to_float32(ds):
    """
    Convert all variables and coordinates in the dataset to float32, except for the time variable.
    
    Parameters:
    ds (xarray.Dataset): The input dataset.

    Returns:
    xarray.Dataset: The dataset with variables and coordinates converted to float32.
    """
    # Convert data variables
    for var in ds.data_vars:
        if var != 'time':  # Exclude the time variable
            ds[var] = ds[var].astype('float32')
    
    # Convert coordinates
    for coord in ds.coords:
        if coord != 'time':  # Exclude the time coordinate
            ds.coords[coord] = ds.coords[coord].astype('float32')
    
    return ds


def process_files(crop_file, cloud_list, var_list):
    """
    Process IR and cloud physical properties files to combine the data.

    Parameters:
    -----------
    crops_list : list of str
        List of file paths to the crop (IR) NetCDF files.
    cloud_list : list of str
        List of file paths to the cloud properties NetCDF files.
    var_list : list of str
        list of the variables to include in the dataset.

    Returns:
    --------
    xr.Dataset
    """
    
    crop_ds = xr.open_dataset(crop_file, decode_times=True)
    #print(crop_ds)

    # Get the time from the IR file
    crop_time = crop_ds['time'].values[0]
    print(crop_time)

    # Find the corresponding cloud file based on the time
    cloud_filepath = find_corresponding_file(cloud_list, crop_time)
    if cloud_filepath is None:
        print(f"No matching cloud file found for time: {crop_time}")

    cloud_ds = xr.open_dataset(cloud_filepath, decode_times=True)
    #print(cloud_ds)

    cloud_ds = convert_to_float32(cloud_ds)

    # Select only the variables in the list
    cloud_ds = cloud_ds[var_list]

    # Select the data within the lat/lon bounds of the IR data
    lat_bounds = crop_ds['lat'].values[[0, -1]]
    lon_bounds = crop_ds['lon'].values[[0, -1]]

    # Create masks for the latitude and longitude conditions
    lat_mask = (cloud_ds['lat'] >= lat_bounds[0]) & (cloud_ds['lat'] <= lat_bounds[1])
    lon_mask = (cloud_ds['lon'] >= lon_bounds[0]) & (cloud_ds['lon'] <= lon_bounds[1])

    # Apply the masks to select the data
    data_ds_sel = cloud_ds.where(lat_mask & lon_mask, drop=True)

    # Select the data for the specific time
    data_ds_sel = data_ds_sel.sel(time=crop_time, method='nearest')

    return data_ds_sel


def save_nc(output_dir, crop_file, ds):

    #output_filename = crop_file
    output_filepath = output_dir+crop_file.split('/')[-1]
    #print(output_filepath)

    # Save the combined dataset to a new NetCDF file
    ds.to_netcdf(output_filepath)
    print(f"Saved combined dataset to {output_filepath}")
    

# Define directories
crop_directory = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc/' #70135?
cloud_directory = '/data/sat/msg/CM_SAF/merged_cloud_properties/'
output_directory = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/'
msg_directory = '/data/sat/msg/netcdf/parallax/'

# Check if the directory exists
if not os.path.exists(output_directory):
    # Create the directory if it doesn't exist
    os.makedirs(output_directory) 


#get list of cloud properties files and crop files
crops_list = sorted(glob(f'{crop_directory}*.nc'))

# Initialize lists to store file paths
clouds_list = []
msg_list = []

years = ['2013', '2014']

# Iterate over the years and gather the files for each year
for year in years:
    clouds_list.extend(sorted(glob(f'{cloud_directory}{year}/*/*.nc')))
    msg_list.extend(sorted(glob(f'{msg_directory}{year}/*/*.nc')))

# Print the lists (optional)
#print("Crops List:", crops_list, len(crops_list)) #33792
#print("Clouds List:", clouds_list, len(clouds_list)) #366
#print("MSG List:", msg_list, len(msg_list)) #366


cloud_vars = ['cph', 'cma', 'cwp', 'cot', 'ctt', 'ctp', 'cth', 'cre']
#msg_vars = ['IR_108', 'WV_062', 'IR_039']

# #loop over the crops
# for crop_file in crops_list:
#     cloud_ds = process_files(crop_file, clouds_list, cloud_vars)
#     #print(cloud_ds)
#     #msg_ds = process_files(crop_file, msg_list, msg_vars)
#     #print(msg_ds)
        
#     save_nc(output_directory, crop_file, cloud_ds)


# Define your processing function
def process_and_save(crop_file):
    cloud_ds = process_files(crop_file, clouds_list, cloud_vars)
    #msg_ds = process_files(crop_file, msg_list, msg_vars)  # Uncomment if needed
    save_nc(output_directory, crop_file, cloud_ds)
    return crop_file  # Optionally return something for tracking progress

# Parallel processing of crops_list
with ProcessPoolExecutor() as executor:
    futures = {executor.submit(process_and_save, crop_file): crop_file for crop_file in crops_list}
    
    # Optionally track progress and handle exceptions
    for future in concurrent.futures.as_completed(futures):
        crop_file = futures[future]
        try:
            data = future.result()
            print(f"Processed and saved: {crop_file}")
        except Exception as e:
            print(f"Error processing {crop_file}: {e}")


#nohup 191582