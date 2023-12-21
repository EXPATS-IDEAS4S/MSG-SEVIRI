"""
Open MSG-SEVIRI nat files fully disk with Satpy 
Crop it to area of interest, project it in latlon grid and convert it to netCDF

author: Daniele Corradini
last Edit: December 2023
"""

##################
#import libraries#
##################

import numpy as np
import pandas as pd
import satpy 
from glob import glob
import xarray as xr
import datetime
import sys
import os
import time

# Start time
begin_time = time.time()

#############
#check Satpy#
#############

#check if satpy has all the dependencies installed
#from satpy.utils import check_satpy
#check_satpy()

#check the readers name available in satpy
#print(satpy.available_readers())
#seviri_l1b_native

##############
#define paths#
##############

# Define the file path 
path_to_file = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_FullDisk/" 

#open all files in directory 
natfile = "MSG4-SEVI-MSG15-0100-NA-*-NA.nat"

#test code with a single file
#h5file = "MSG4-SEVI-MSG15-0100-NA-20210714121243.449000000Z-NA.nat"

fnames = glob(path_to_file+natfile)
#print(fnames)


###############
#Quality Check#
###############

# #check for corrupted files
# not_corrupted_files = Data_Preprocessing_Functions.check_openable_files(path_to_file,fnames,'agri_fy4a_l1')
# print('Number of files that are corrupted:', len(fnames)-len(not_corrupted_files))

# #check for missing time steps
# missing_intervals = Data_Preprocessing_Functions.check_file_coverage(path_to_file, fnames,'202010010000','202010312359')
# print('Number of missing intervals:', len(missing_intervals))

###########
#Open Data#
###########

open_data = True

if open_data:

    #2021 Germany Flood Area
    lonmin, latmin, lonmax, latmax= 5, 48, 9, 52

    #check for nan values, inizialize array
    #nan_values = []
    #start_nan = []
    #end_nan = []

    #Read data at different temporal steps
    for t,f in enumerate(fnames):
        file = f.split('/')[-1]
        #print(file)

        #get start and end time from filename format yyyymmddhhmmss
        end_scan_time = file.split('-')[5].split('.')[0]
        time_str = datetime.datetime.strptime(end_scan_time, "%Y%m%d%H%M%S")
        print(time_str)
        #end_time = file.split('-')[10]

        #append date for nan checking
        #start_nan.append(datetime.datetime.strptime(start_time, "%Y%m%d%H%M%S"))
        #end_nan.append(datetime.datetime.strptime(end_time, "%Y%m%d%H%M%S"))
        
        #open file with Satpy
        scn = satpy.Scene(reader='seviri_l1b_native', filenames=[f]) #By default bad quality scan lines are masked and replaced with np.nan based on the quality flags provided by the data 
        
        #get the channel names
        channels = scn.available_dataset_names() 
        #['HRV', 'IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']

        #inizialize list for nan values for each channel
        #nan_channels = []

        #get the lat/lon coords

        #Load one channel
        scn.load(['IR_016'])       

        #Crop to Vietnam area
        crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

        #get coord in the cropped area
        area_crop = crop_scn['IR_016'].attrs['area'] #area in m
        sat_lon_crop, sat_lat_crop = area_crop.get_lonlats() #lat/lon grid (438,246)

        # create DataArrays with the coordinates using cloud mask grid
        lon_da = xr.DataArray(sat_lon_crop, dims=("y", "x"), name="lon grid")
        lat_da = xr.DataArray(sat_lat_crop, dims=("y", "x"), name="lat grid")

        # combine DataArrays into xarray object
        ds = xr.Dataset({"lon grid": lon_da, "lat grid": lat_da})

        #print(ds)

        #esclude HRV channel
        channels = channels[1:]

        #loop over the channels #1-6 reflectance; 7-14 TB -> reflectance only for shortwave
        #TODO channels loop can be parallelized as the order is not important, use dask or multiporcessing 
        for ch in channels:
            #Load channel
            scn.load([ch])       

            #Crop to Vietnam area
            crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

            #get data in the cropped area
            sat_data_crop = crop_scn[ch].values #R/Tb

            #check grid
            #print(Data_Preprocessing_Functions.check_regular_grid(sat_lon_crop,sat_lat_crop,'lat',True))
            #print(Data_Preprocessing_Functions.check_regular_grid(sat_lon_crop,sat_lat_crop,'lon',True))
        
            #check for missing data
            #nan_channels.append(np.sum(np.isnan(sat_data_crop))/len(sat_data_crop)) #take the ratio of nan and the total number of pixels
            
            #add channel values to the Dataset
            sat_da = xr.DataArray(sat_data_crop, dims=("y", "x"), name=str(ch))
            ds[str(ch)] = sat_da

        #append the list of nan values for all the channels
        #nan_values.append(nan_channels)

        # Add a new dimension for the start time coordinate
        ds = ds.expand_dims('end_time', axis=0)
        ds['end_time'] = [time_str]

        # Set the directory path to save files
        proj_file_path = path_to_file+'HRSEVIRI_20210712_20210715_Processed/'

        # Check if the directory exists
        if not os.path.exists(proj_file_path):
            # Create the directory if it doesn't exist
            os.makedirs(proj_file_path)

        #save the features using a similar name of the HDF5 file but in netCDF format
        ds.to_netcdf(proj_file_path+f.split('/')[-1].split('.')[0]+'.nc')
        print('product saved\n')
        
        print(ds)

          
    ######################
    #check missing values#
    ######################

    #convert to dataframe table the nan lists
    #df_nan = pd.DataFrame(nan_values, columns=channels)

    #add times
    #df_nan['Start Time'] = start_nan

    #save to csv file
    #df_nan.to_csv(path_to_file+'nan_ratio.csv', index=False)
    
    #df_nan = pd.read_csv(path_to_file+'nan_ratio.csv')

    #plot number of nan values (ratio) for each channel and time step
    #Data_Preprocessing_Functions.plot_nan_ratio(df_nan,path_to_file) 


# End time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - begin_time
# Path to the text file where you want to save the elapsed time
output_file_path = path_to_file+'elapsed_time_satpy.txt'

# Write elapsed time to the file
with open(output_file_path, 'w') as file:
    print(f"Elapsed time: {elapsed_time} seconds", file=file)