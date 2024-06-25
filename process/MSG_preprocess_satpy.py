"""
Open MSG-SEVIRI files with Satpy 
Crop it to area of interest, 
project it in latlon grid 
and convert it to netCDF
if needed perfrom parallax correction
and regrid the data in a regular lat-lon grid

@author: Daniele Corradini

TODO: check for missing timestamps once the daily dataset has been created
TODO: better handle inizialization of dataset for native grid 
"""
import satpy 
from glob import glob
import xarray as xr
from datetime import datetime, timedelta
import os
import time
import numpy as np
import warnings


#Import parameters from config file and custom methods
from config_satpy_process import path_to_file, path_to_cth, natfile, cth_file, path_to_save
from config_satpy_process import lonmin, lonmax, latmax, latmin, channels, step_deg, interp_method
from config_satpy_process import parallax_correction, regular_grid
from config_satpy_process import msg_reader, cth_reader
from regrid_functions import regrid_data, fill_missing_data_with_interpolation, generate_regular_grid

# list of custom methods

def compute_timestamps_from_time_range(start_date, end_date):
    """
    Compute a list of timestamps given the time range,
    considering a time interval of 15 minutes (4 files per hour, 96 files per day).
    end date is excluded!
    """
    # Format the dates
    start = datetime.strptime(start_date, "%Y.%m.%d")
    end = datetime.strptime(end_date, "%Y.%m.%d")
    
    # Correct for the end date being earlier in the year than the start date
    if end < start:
        print('End date cannot happen before the start date!')
        return []
    else:
        # Initialize the current time at the start date
        current_time = start
        timestamps = []
        
        # Generate timestamps at 15-minute intervals until the end date
        while current_time <= end:
            timestamps.append(current_time)
            current_time += timedelta(minutes=15)
        
        return timestamps
    
def check_filelist(filelist1, filelist2, name1, name2):
    """
    chck if the number of files in 2 filelists are the same
    """
    if len(filelist1)==len(filelist2):
        return print(f'{name1} has same number of files of {name2}, {len(filelist1)}')
    elif len(filelist1)>len(filelist2):
        return print(f'{name1} has more files, {len(filelist1)}')
    else:
        return print(f'{name2} has more files, {len(filelist2)}')
    

def get_datetime_msg(filename):
    """
    get date and time from filename
    example filename: MSG4-SEVI-MSG15-0100-NA-20190401001243.703000000Z-NA.subset.nat
    """
    #get start and end time from filename format yyyymmddhhmmss
    end_scan_time = filename.split('-')[5].split('.')[0]
    #print(end_scan_time)
    min_str = end_scan_time[10:12]
    #print(min_str)
    #switch the minutes that indicate the end the scan to the minutes that indicate the 'rounded' start of the scan
    if '00'<min_str<'15': min_str='00'
    if '15'<min_str<'30': min_str='15' 
    if '30'<min_str<'45': min_str='30'
    if '45'<min_str<'59': min_str='45'
    time_str = end_scan_time[0:10]+min_str
    time_str = datetime.strptime(time_str, "%Y%m%d%H%M")

    return time_str


def get_datetime_cth(filename):
    """
    get date and time from filename of cth files
    example filename: CTXin20190401000000405SVMSG01UD.nc
    """
    time_str = filename.split('.')[0][5:17]
    time_str = datetime.strptime(time_str, "%Y%m%d%H%M")

    return time_str


def extract_timestamps(filenames, type):
    """
    Extracts and returns a list of timestamps from a list of filenames.
    """
    timestamps = []
    for filename in filenames:
        if type == 'msg':
            timestamp = get_datetime_msg(filename.split('/')[-1])
        elif type == 'cth':
            timestamp = get_datetime_cth(filename.split('/')[-1])
        else:
            print('wrong type name!')
        timestamps.append(timestamp)
    
    return timestamps


def filter_timestamps(timestamps, base_directory):
    """
    Filters out timestamps that fall on dates for which data has already been converted.
    
    Args:
    timestamps: A list of timestamps to check.
    base_directory: The base directory where the converted files are stored.
    
    Returns:
    A list of timestamps that are not on dates with converted files.
    """

    date = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ').date()
    year, month, day = date.year, date.month, date.day

    filename = f'{year:04d}{month:02d}{day:02d}-EXPATS-RG.nc'
    file_path = os.path.join(base_directory, str(year), f'{month:02d}', filename)
    
    clean_timestamps = []
    
    for timestamp in timestamps:
        if not os.path.isfile(file_path):
            clean_timestamps.append(timestamp)
    
    return clean_timestamps


def get_channel(channels, idx, parallax):
    ch = channels[idx]
    if parallax:
        ch = 'parallax_corrected_'+channels[ch_idx]

    return ch


def find_all_indices(lst, value):
    """
    Returns a list of all indices of value in lst.
    
    Args:
    lst: The list to search.
    value: The value to search for.

    Returns:
    A list of indices where value is found in lst.
    """
    return [index for index, element in enumerate(lst) if element == value]


def find_highest_index(lst, value):
    """
    Returns the highest index of value in lst.
    
    Args:
    lst: The list to search.
    value: The value to search for.

    Returns:
    The highest index where value is found in lst, or raises ValueError if not found.
    """
    indices = find_all_indices(lst, value)
    if indices:
        return max(indices)
    else:
        raise ValueError

def find_common_timestamp_position(timestamp, list1, list2):
    """
    Checks if a given timestamp is present in both provided lists and returns the highest positions
    in each list if found. If the timestamp is not found in either list, returns None.

    Args:
    timestamp: The timestamp to search for.
    list1: First list of timestamps.
    list2: Second list of timestamps.

    Returns:
    A tuple containing the highest positions in list1 and list2, or None if not found in both.
    """
    try:
        pos1 = find_highest_index(list1, timestamp)  # Find the highest index in list1
        pos2 = find_highest_index(list2, timestamp)  # Find the highest index in list2
        return (pos1, pos2)
    except ValueError:
        # This block is executed if the timestamp is not found in either list
        return None
    

def open_satpy_scene(file_msg, file_cth, msg_reader, cth_reader, parallax):
    """
    Initializes a Satpy Scene object for satellite data visualization or processing.
    This function configures the scene with specified readers for MSG and CTH files,
    handling file inputs and conditionally incorporating parallax correction.

    Parameters:
    file_msg (str): Path to the MSG file used for the scene.
    file_cth (int): Index in a filename list for the CTH file to be included in the scene.
    msg_reader (str): Identifier for the reader configured for MSG files.
    cth_reader (str): Identifier for the reader configured for CTH files.
    parallax (bool): Flag to determine if parallax correction should be applied. When True,
                     both MSG and CTH data are used with respective readers. If False,
                     only MSG data is used with its reader.

    Returns:
    satpy.Scene: Configured Satpy Scene object ready for further processing or visualization.
                 By default, bad quality scan lines are masked and replaced with np.nan,
                 based on the quality flags provided by the data.
    """
    if parallax:
        scn = satpy.Scene({msg_reader: [file_msg], cth_reader: [file_cth]})
    else:
        scn = satpy.Scene(reader=msg_reader, filenames=[file_msg])

    return scn


def compress_and_save(ds, proj_file_path, filename_save):
    """
    Compresses and saves an xarray dataset in the netCDF format with specified compression settings.

    Parameters:
    ds (xarray.Dataset): The dataset to be saved.
    proj_file_path (str): The directory path where the netCDF file will be saved. If the directory
                          does not exist, it will be created.
    filename (str): The base name for the output file. The output filename will be derived from this,
                    removing any directory path and changing the extension to '.nc'.
    """

    # Check if the directory exists
    if not os.path.exists(proj_file_path):
        # Create the directory if it doesn't exist
        os.makedirs(proj_file_path)

    #save the features using a similar name of the HDF5 file but in netCDF format
    #ds.to_netcdf(proj_file_path+filename_save)
    ds.to_netcdf(proj_file_path+filename_save, \
        encoding={'IR_016':{"zlib":True, "complevel":9},\
                'IR_039':{"zlib":True, "complevel":9},\
                'IR_087':{"zlib":True, "complevel":9},\
                'IR_097':{"zlib":True, "complevel":9},\
                'IR_108':{"zlib":True, "complevel":9},\
                'IR_120':{"zlib":True, "complevel":9},\
                'IR_134':{"zlib":True, "complevel":9},\
                'VIS006':{"zlib":True, "complevel":9},\
                'VIS008':{"zlib":True, "complevel":9},\
                'WV_062':{"zlib":True, "complevel":9},\
                'WV_073':{"zlib":True, "complevel":9},\
                'time':{"units": "seconds since 2000-01-01", "dtype": "i4"}})
    print('product saved\n')


def initialize_empty_dataset(channels, lat_arr, lon_arr, regular_grid):
    """
    Initializes an empty xarray Dataset with specified channels and spatial coordinates,
    optionally using a regular grid layout. Each channel is filled with NaN values and
    the dataset includes a 'time' dimension expanded along the first axis.

    Parameters:
    channels (list of str): List of channel names to be included as variables in the dataset.
    lat_arr (array-like): Array of latitude values used as coordinates.
    lon_arr (array-like): Array of longitude values used as coordinates.
    regular_grid (bool): If True, initializes each channel with the given latitude and
                         longitude arrays as a regular grid. If False, no channels are
                         initialized, but the dataset still expands a 'time' dimension.

    Returns:
    xarray.Dataset: A dataset with dimensions ('time', 'y', 'x') where each channel variable
                    is initialized with NaN values across the spatial dimensions. The dataset
                    includes coordinates for 'lat' and 'lon', and a singleton 'time' dimension
                    is added.
    """
    ds = xr.Dataset()
    if regular_grid:
        for channel in channels:
            data_array = xr.DataArray(
                    np.full((len(lat_arr), len(lon_arr)), np.nan, dtype='float32'),
                    dims=("y", "x"),
                    coords={"lat": ("y", lat_arr.astype(np.float32)), "lon": ("x", lon_arr.astype(np.float32))},
                    name=channel
                    )
            ds[channel] = data_array         
    
    ds = ds.expand_dims('time', axis=0)

    return ds


def create_dataset_with_lat_lon_dimensions(channels, lat_arr, lon_arr, regular_grid=True):
    # Create an empty Dataset
    ds = xr.Dataset()

    if regular_grid:
        # Loop through each channel and create a DataArray with lat and lon as dimensions
        for channel in channels:
            # Create a DataArray filled with NaN values
            data_array = xr.DataArray(
                np.full((len(lat_arr), len(lon_arr)), np.nan, dtype='float32'),
                dims=("lat", "lon"),  # Set dimensions to lat and lon
                coords={
                    "lat": (["lat"], lat_arr.astype(np.float32)),  # Define latitude coordinate
                    "lon": (["lon"], lon_arr.astype(np.float32))   # Define longitude coordinate
                },
                name=channel
            )
            # Add the DataArray to the Dataset
            ds[channel] = data_array

    # Expand dimensions to add a 'time' dimension, setting the axis to 0
    ds = ds.expand_dims('time', axis=0)

    return ds


def check_file_exists(folder_path, filename):
    """
    Check if a specific file exists within a given folder.
    
    Args:
    folder_path (str): The path to the folder where the file might be located.
    filename (str): The name of the file to check.
    
    Returns:
    bool: True if the file exists, False otherwise.
    """
    # Combine the folder path and filename to create the full path to the file
    file_path = os.path.join(folder_path, filename)
    
    # Check if the file exists at the specified path
    return os.path.exists(file_path)


def get_filename_and_path(timestamp, parallax_correction, path_to_save):
    year_save = timestamp.strftime("%Y")
    month_save = timestamp.strftime("%m")
    day_save = timestamp.strftime("%d")
    proj_file_path = path_to_save+"noparallax/"+year_save+"/"+month_save+"/"
    if parallax_correction:
        proj_file_path = path_to_save+"parallax/"+year_save+"/"+month_save+"/"
    filename = year_save + month_save + day_save + '-EXPATS-RG.nc'

    return proj_file_path, filename



if __name__ == "__main__":

    # Ignore specific warnings by message
    warnings.filterwarnings("ignore", message="You will likely lose important projection information when converting to a PROJ string from another format.")
    warnings.filterwarnings("ignore", message="Overlap checking not implemented. Waiting for fix for https://github.com/pytroll/pyresample/issues/329")

    # Start time
    begin_time = time.time()

    year = "2020"
    month = "06" #use "*" if all months considered
    begin_date = year+'.06.01'
    end_date = year+'.07.01' #end point is excluded

    timestamps = compute_timestamps_from_time_range(begin_date,end_date)   
    print(f'total number of timestamps in {begin_date}-{end_date}: {len(timestamps)}')

    #open all MSG files in directory 
    path_pattern = f"{path_to_file}{year}/{month}/*/{natfile}"
    fnames = sorted(glob(path_pattern))    

    #open all CTH files in directoy 
    path_pattern_cth = f"{path_to_cth}{year}/{month}/*/{cth_file}"
    cth_fnames = sorted(glob(path_pattern_cth))
    
    #extract timestamps
    msg_timestamps = extract_timestamps(fnames,'msg')
    cth_timestamps = extract_timestamps(cth_fnames, 'cth')

    #TODO create a function that remore the timestamps of the file already converted

    check_filelist(msg_timestamps, cth_timestamps, 'msg_timestamps', 'cth_timestamps')

    #find a regular grid
    if regular_grid:
        lat_arr,  lon_arr = generate_regular_grid(latmin,latmax,lonmin,lonmax,step_deg,path_to_file)
        
        # Generate grid points
        lat_reg_grid, lon_reg_grid = np.meshgrid(lat_arr, lon_arr, indexing='ij')

    # initialize day variable
    last_day = '00'
    count = 0 

    #Read data at different temporal steps (use cth because complete)
    for t, timestamp in enumerate(timestamps):
        # count over the loop
        print(f'Processing file number {t+1}/{len(timestamps)}')
        print(f'Current timestamp: {timestamp}')

        #extract day from time string
        day = timestamp.strftime("%d")

        #create an empty dataset
        ds = create_dataset_with_lat_lon_dimensions(channels, lat_arr, lon_arr, regular_grid)

        #add timestamp to dataset
        ds['time'] = [timestamp] 

        #check if cth and msg exist for the corresponding timestamp
        positions = find_common_timestamp_position(timestamp,msg_timestamps,cth_timestamps)
        
        if positions:
            file_msg = fnames[positions[0]]
            #print(file_msg)
            file_cth = cth_fnames[positions[1]]
            #print(file_cth)
            scn = open_satpy_scene(file_msg,file_cth,msg_reader,cth_reader,parallax_correction)
            
            # loop over the channels 
            for ch_idx in range(len(channels)):
                #Load one channel
                ch = get_channel(channels,ch_idx,parallax_correction)
                scn.load([ch]) 

                #Crop to area of interest
                crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

                #get the lat/lon coordsonly for one channel (as all of them share the same grid)
                if ch_idx==0:
                    #get coord in the cropped area
                    area_crop = crop_scn[ch].attrs['area'] #area in m
                    sat_lon_crop, sat_lat_crop = area_crop.get_lonlats() 
                    #print(np.shape(sat_lat_crop),sat_lat_crop)
                    #print(np.shape(sat_lon_crop),sat_lon_crop)

                    if not regular_grid:
                        # create DataArrays with the coordinates using cloud mask grid
                        lon_da = xr.DataArray(sat_lon_crop.astype(np.float32), dims=("y", "x"), name="lon_grid")
                        lat_da = xr.DataArray(sat_lat_crop.astype(np.float32), dims=("y", "x"), name="lat_grid")

                        # combine DataArrays into xarray object
                        ds["lon_grid"] = lon_da
                        ds["lat_grid"] = lat_da
                        #print(ds)

                #get data in the cropped area
                sat_data_crop = crop_scn[ch].values #R/Tb
                #print('sat data',sat_data_crop)

                if regular_grid:
                    #interpolate the missing points (NaN)
                    sat_data_crop = fill_missing_data_with_interpolation(sat_lat_crop, sat_lon_crop, sat_data_crop)
                    
                    #regrid the sat data to a regular grid
                    sat_data_crop = regrid_data(sat_lat_crop, sat_lon_crop, sat_data_crop, lat_reg_grid, lon_reg_grid, interp_method) 
                    
                    #add channel values to the Dataarray
                    sat_da = xr.DataArray(
                    sat_data_crop.astype(np.float32),
                    #dims=("y", "x"),
                    #coords={"lat": ("y", lat_arr.astype(np.float32)), "lon": ("x", lon_arr.astype(np.float32))},
                    dims=("lat", "lon"),  # Set dimensions to lat and lon
                    coords={
                        "lat": (["lat"], lat_arr.astype(np.float32)),  # Define latitude coordinate
                        "lon": (["lon"], lon_arr.astype(np.float32))   # Define longitude coordinate
                    },
                    name=channels[ch_idx]
                    )

                else:        
                    sat_da = xr.DataArray(sat_data_crop, dims=("y", "x"), name=channels[ch_idx])
                
                #add channel values to the Dataset
                ds[channels[ch_idx]] = sat_da
        else:
            print(f'missing timestamps: {t}')      
        
        if day == last_day:
            ds_day = xr.concat([ds_day, ds], dim='time')
        else:
            if count>0:
                #save the daily dataset 
                proj_file_path, filename = get_filename_and_path(timestamps[t-1],parallax_correction,path_to_save)
                print(filename)
                compress_and_save(ds_day,proj_file_path,filename)
                #update dataset with the next day
            ds_day = ds
        count+=1
            

        #print(ds_day)
        #update last day
        last_day = day   
    
    print('Processing concluded!')

    # End time
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - begin_time
    # Path to the text file where you want to save the elapsed time
    output_file_path = '/home/dcorradi/Documents/Codes/MSG-SEVIRI/process/log/elapsed_time_satpy.txt'

    # Write elapsed time to the file
    with open(output_file_path, 'w') as file:
        print(f"Elapsed time: {elapsed_time} seconds", file=file)