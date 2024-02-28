"""
Open MSG-SEVIRI nat files fully disk with Satpy 
Crop it to area of interest, project it in latlon grid and convert it to netCDF

author: Daniele Corradini
last Edit: December 2023
"""

##################
#import libraries#
##################

import satpy 
from glob import glob
import xarray as xr
import datetime
import os
import time

# Start time
begin_time = time.time()

#Import parameters from config file
from config_satpy_process import path_to_file, path_to_cth, natfile, cth_file
from config_satpy_process import lonmin, lonmax, latmax, latmin, channels, parallax_correction
from config_satpy_process import msg_reader, cth_reader

#open all MSG files in directory 
fnames = sorted(glob(path_to_file+natfile))
print(fnames)

#open all CTH files in directoy
cth_fnames = sorted(glob(path_to_cth+cth_file))

#Read data at different temporal steps
for t,f in enumerate(fnames):
    # count over the loop
    print(f'Processing file number {t+1}/{len(fnames)})')

    #get start and end time from filename format yyyymmddhhmmss
    end_scan_time = f.split('/')[-1].split('-')[5].split('.')[0]
    time_str = datetime.datetime.strptime(end_scan_time, "%Y%m%d%H%M%S")
    print(time_str)
    
    # Define Scene to open file with Satpy
    scn = satpy.Scene(reader=msg_reader, filenames=[f]) #By default bad quality scan lines are masked and replaced with np.nan based on the quality flags provided by the data 
    ch = channels[0]

    if parallax_correction:
        scn = satpy.Scene({msg_reader: [f], cth_reader: [cth_fnames[t]]})
        ch = 'parallax_corrected_'+ch
    
    
    #TODO channels loop can be parallelized as the order is not important, use dask or multiporcessing 
    for ch_idx,ch in enumerate(channels):
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

            # create DataArrays with the coordinates using cloud mask grid
            lon_da = xr.DataArray(sat_lon_crop, dims=("y", "x"), name="lon_grid")
            lat_da = xr.DataArray(sat_lat_crop, dims=("y", "x"), name="lat_grid")

            # combine DataArrays into xarray object
            ds = xr.Dataset({"lon_grid": lon_da, "lat_grid": lat_da})
            #print(ds)

        #get data in the cropped area
        sat_data_crop = crop_scn[ch].values #R/Tb
        #print('sat data',sat_data_crop)
        
        #add channel values to the Dataset
        sat_da = xr.DataArray(sat_data_crop, dims=("y", "x"), name=str(ch))
        ds[str(ch)] = sat_da

    # Add a new dimension for the start time coordinate
    ds = ds.expand_dims('end_time', axis=0)
    ds['end_time'] = [time_str]

    # Set the directory path to save files
    proj_file_path = path_to_file+'Processed/'
    if parallax_correction:
        proj_file_path = path_to_file+'Parallax_Corrected/'

    # Check if the directory exists
    if not os.path.exists(proj_file_path):
        # Create the directory if it doesn't exist
        os.makedirs(proj_file_path)

    #save the features using a similar name of the HDF5 file but in netCDF format
    ds.to_netcdf(proj_file_path+f.split('/')[-1].split('.')[0]+'.nc')
    print('product saved\n')
    
    #print(ds)

# End time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - begin_time
# Path to the text file where you want to save the elapsed time
output_file_path = path_to_file+'elapsed_time_satpy.txt'

# Write elapsed time to the file
with open(output_file_path, 'w') as file:
    print(f"Elapsed time: {elapsed_time} seconds", file=file)



# # storing ncdf data compressed mode: example!
#     MRRdata.to_netcdf(path_out+dateReverse+‘_MRR_PRO_msm_eurec4a.nc’, encoding={“Z”:{“zlib”:True, “complevel”:9},\
#                                                                                              “Ze”: {“dtype”: “f4", “zlib”: True, “complevel”:9}, \
#                                                                                              “Zea”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “drop_size_distribution”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “liquid_water_content”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “Kurtosis”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “fall_speed”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “skewness”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “mean_mass_weigthed_raindrop_diameter”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “spectral_width”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “rain_rate”: {“zlib”: True, “complevel”:9}, \
#                                                                                              “lat”: {“dtype”: “f4"} , \
#                                                                                              “lon”: {“dtype”: “f4”}, \
#                                                                                              “time”: {“units”: “seconds since 2020-01-01", “dtype”: “i4"}})