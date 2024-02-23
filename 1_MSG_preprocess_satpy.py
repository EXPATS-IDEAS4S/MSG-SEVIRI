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
path_to_file = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_Flood_domain_DataTailor_nat/" 
path_to_cth = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/NWC_SAF/" 

#open all MSG files in directory 
natfile = "MSG4-SEVI-MSG15-*-NA.subset.nat"
fnames = sorted(glob(path_to_file+natfile))
print(fnames)

#open all CTH files in directoy
#cth_file = 'CTXin*.nc'
cth_file = "S_NWC_CTTH*.nc"
cth_fnames = sorted(glob(path_to_cth+cth_file))

scn = satpy.Scene({"seviri_l1b_native": [f], "nwcsaf-geo_nc": [cth_fnames[t]]})



###########
#Open Data#
###########

open_data = True
parallax_correction = True

if open_data:

    #2021 Germany Flood Area
    lonmin, latmin, lonmax, latmax= 5, 48, 9, 52

    #Read data at different temporal steps
    for t,f in enumerate(fnames):
        file = f.split('/')[-1]
        #print(file)

        #get start and end time from filename format yyyymmddhhmmss
        end_scan_time = file.split('-')[5].split('.')[0]
        time_str = datetime.datetime.strptime(end_scan_time, "%Y%m%d%H%M%S")
        print(time_str)

        cth_file = cth_fnames[t].split('/')[-1]

        
        #open file with Satpy
        scn = satpy.Scene(reader='seviri_l1b_native', filenames=[f]) #By default bad quality scan lines are masked and replaced with np.nan based on the quality flags provided by the data 
        
        #get the channel names
        channels = scn.available_dataset_names() 
        #print(channels)
        #['HRV', 'IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']

        #get the lat/lon coords

        #Load one channel
        scn.load(['IR_039'])       

        #Crop to area of interest
        crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

        #get coord in the cropped area
        area_crop = crop_scn['IR_039'].attrs['area'] #area in m
        sat_lon_crop, sat_lat_crop = area_crop.get_lonlats() #lat/lon grid (77,104)
        #print(np.shape(sat_lat_crop),sat_lat_crop)
        #print(np.shape(sat_lon_crop),sat_lon_crop)

        #get coords with parallax correction
        #sc = satpy.Scene({"seviri_l1b_hrit": files_l1b, "nwcsaf-geo": files_l2})
        #sc.load(["parallax_corrected_VIS006"])
        #get coord parallax corrected
        #area_plax_corr = sc['VIS006'].attrs['area'] #area in m
        #sat_lon_plax, sat_lat_plax = area_plax_corr.get_lonlats() #lat/lon grid (77,104)

        # create DataArrays with the coordinates using cloud mask grid
        lon_da = xr.DataArray(sat_lon_crop, dims=("y", "x"), name="lon grid")
        lat_da = xr.DataArray(sat_lat_crop, dims=("y", "x"), name="lat grid")

        # combine DataArrays into xarray object
        ds = xr.Dataset({"lon grid": lon_da, "lat grid": lat_da})
        #print(ds)
        
        #esclude HRV channel
        channels = channels[1:]

        if parallax_correction:
            #create Scene for the parallax correction
            #scn = satpy.Scene({"seviri_l1b_native": [f], "cmsaf-claas2_l2_nc": [cth_fnames[t]]})
            scn = satpy.Scene({"seviri_l1b_native": [f], "nwcsaf-geo_nc": [cth_fnames[t]]})

        #TODO channels loop can be parallelized as the order is not important, use dask or multiporcessing 
        for ch in channels:
            if parallax_correction:
                ch = 'parallax_corrected_'+ch

            #Load channel
            scn.load([ch])       

            #Crop to area of interest
            crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

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
        proj_file_path = path_to_file+'HRSEVIRI_20210712_20210715_Processed/'
        if parallax_correction:
            proj_file_path = path_to_file+'HRSEVIRI_20210712_20210715_Parallax_Corrected/'

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