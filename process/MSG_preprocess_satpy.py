"""
Open MSG-SEVIRI files with Satpy 
Crop it to area of interest, 
project it in latlon grid 
and convert it to netCDF
if needed perfrom parallax correction
and regrid the data in a regular lat-lon grid

@author: Daniele Corradini

#TODO: cth have all timestamps while nat doesn't have
so in case nat is missing fill the timestamps with Nan and save the netcdf daily

"""
import satpy 
from glob import glob
import xarray as xr
import datetime
import os
import time
import numpy as np

#Import parameters from config file and custom methods
from config_satpy_process import path_to_file, path_to_cth, natfile, cth_file
from config_satpy_process import lonmin, lonmax, latmax, latmin, channels, step_deg, interp_method
from config_satpy_process import parallax_correction, regular_grid
from config_satpy_process import msg_reader, cth_reader
from regrid_functions import regrid_data, fill_missing_data_with_interpolation, generate_regular_grid

# list of custom methods

def compute_timestamps_from_time_range(start_date, end_date):
    """
    Compute a list of timestamps given the time range,
    considering a time interval of 15 minutes (4 files per hour, 96 files per day).
    """
    # Format the dates
    start = datetime.datetime.strptime(start_date, "%y.%m.%d")
    end = datetime.datetime.strptime(end_date, "%y.%m.%d")
    
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
            current_time += datetime.timedelta(minutes=15)
        
        return timestamps
    
def check_filelist(filelist1, filelist2, name1, name2):
    """
    chck if the number of files in 2 filelists are the same
    """
    if len(filelist1)>len(filelist2):
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
    time_str = datetime.datetime.strptime(time_str, "%Y%m%d%H%M")

    return time_str


def get_datetime_cth(filename):
    """
    get date and time from filename of cth files
    example filename: CTXin20190401000000405SVMSG01UD.nc
    """
    time_str = filename.split('.')[0][5:17]
    time_str = datetime.datetime.strptime(time_str, "%Y%m%d%H%M")

    return time_str

def extract_timestamps(filenames, type):
    """
    Extracts and returns a list of timestamps from a list of filenames.
    """
    timestamps = []
    for filename in filenames:
        if type == 'msg':
            timestamp = get_datetime_msg(filename)
        elif type == 'cth':
            timestamp = get_datetime_cth(filename)
        else:
            print('wrong type name!')
        timestamps.append(timestamp)
    
    return timestamps

if __name__ == "__main__":

    # Start time
    begin_time = time.time()

    year = '2023'
    begin_date = year+'.04.01'
    end_date = year+'.09.30'

    timestamps = compute_timestamps_from_time_range(begin_date,end_date)

    path_to_save = "/data/sat/msg/netcdf/"

    # Construct the path pattern to include subdirectories for days
    path_pattern = f"{path_to_file}{year}/*/*/{natfile}"
    print(path_pattern)

    #open all MSG files in directory 
    fnames = sorted(glob(path_pattern))

    #extract just the timestamps
    msg_timestamps = extract_timestamps(fnames,'msg')

    #open all CTH files in directoy 
    path_pattern_cth = f"{path_to_cth}{year}/*/*/{cth_file}"
    cth_fnames = sorted(glob(path_pattern_cth))
    #print(cth_fnames)

    #extract timestamps
    cth_timestamps = extract_timestamps(cth_fnames, 'cth')

    check_filelist(fnames, cth_fnames, 'msg_filelist', 'cth_filelist')

    #find a regular grid
    if regular_grid:
        lat_arr,  lon_arr = generate_regular_grid(latmin,latmax,lonmin,lonmax,step_deg,path_to_file)
        
        # Generate grid points
        lat_reg_grid, lon_reg_grid = np.meshgrid(lat_arr, lon_arr, indexing='ij')


    #Read data at different temporal steps (use cth because complete)
    for t, timestamp in enumerate(timestamps):
        print(timestamp)
        # count over the loop
        print(f'Processing file number {t+1}/{len(timestamps)}')

        #create empty Dataset
        ds = xr.Dataset()

        #check if cth and msg exist for the corresponding timestamp
        if (timestamp in msg_timestamps) and (timestamp in cth_timestamps):
        
            # Define Scene to open file with Satpy
            scn = satpy.Scene(reader=msg_reader, filenames=[f]) #By default bad quality scan lines are masked and replaced with np.nan based on the quality flags provided by the data 

            if parallax_correction:
                scn = satpy.Scene({msg_reader: [f], cth_reader: [cth_fnames[t]]})
            
            # loop over the channels 
            for ch_idx in range(len(channels)):
                ch = channels[ch_idx]
                if parallax_correction:
                    ch = 'parallax_corrected_'+channels[ch_idx]
                #Load one channel
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
                        #ds = xr.Dataset({"lon_grid": lon_da, "lat_grid": lat_da})
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
                    dims=("y", "x"),
                    coords={"lat": ("y", lat_arr.astype(np.float32)), "lon": ("x", lon_arr.astype(np.float32))},
                    name=str(channels[ch_idx])
                    )

                else:        
                    sat_da = xr.DataArray(sat_data_crop, dims=("y", "x"), name=str(channels[ch_idx]))
                
                #add channel values to the Dataset
                ds[str(channels[ch_idx])] = sat_da
        else:
            #create empty dataset

        # Add a new dimension for the start time coordinate
        ds = ds.expand_dims('time', axis=0)
        ds['time'] = [time_str]

        #extract day from time string
        day = time_str.strftime("%d")
        print(day)

        exit()

        # Set the directory path to save files
        proj_file_path = path_to_save+'noparallax/'+year+'/'+month+'/'+day+'/'
        if parallax_correction:
            proj_file_path = path_to_save+'parallax/'+year+'/'+month+'/'+day+'/'

        # Check if the directory exists
        if not os.path.exists(proj_file_path):
            # Create the directory if it doesn't exist
            os.makedirs(proj_file_path)

        # Set the filename for saving
        filename_save = f.split('/')[-1].split('.')[0]+'.nc'
        if regular_grid:
            filename_save = f.split('/')[-1].split('.')[0]+'_regular_grid.nc'

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
        
        #print(ds)
        #exit()

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