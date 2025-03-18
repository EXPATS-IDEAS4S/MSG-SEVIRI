"""
Processing CTH data from CMSAF to make it compatible to Satpy for the parallax correction

@author: Daniele Corradini
"""
# %%
from glob import glob
import xarray as xr
import os
import numpy as np

# %%
### Define Paths ###

#path where cth data are stored
path_to_files = '/data/sat/msg/CM_SAF/CTX'

#Path output
path_out = '/data/sat/msg/CM_SAF/CTH_processed'

nc_file = "CTX*.nc" #'CTXin20210712000000405SVMSGI1UD.nc'

# %%
def process_cth_files_of_month(year, month):

    #open all files in directory 
    fnames = sorted(glob(f"{path_to_files}/{year:04d}/{month:02d}/*/{nc_file}"))
    
    # get all files that are already processed
    files_processed = sorted(glob(f"{path_out}/{year:04d}/{month:02d}/*/{nc_file}"))

    fnames_processed = [os.path.basename(f) for f in files_processed]
    missing_files = [f for f in fnames if os.path.basename(f) not in fnames_processed]

    # CTXin20130401234500405SVMSG01UD.nc
    # get files in CTX folder that are not present in CTH_processed folder
    # fnames_to_process = list(set(fnames) - set(fnames_processed))
    if len(missing_files) > 0:
        print("----", year, month)
        print(f"{len(missing_files)} files need to be processed")

        # loop over missing files and process them for satpy usage
        for t, f in enumerate(missing_files):
            if t%100==0:
                print(f"{t}/{len(missing_files)}")
            process_single_cth_file(f)

def process_single_cth_file(f):

    #get time
    time = f.split('/')[-1].split('.')[0][5:13]
    #print(time)
    month = time[4:6]
    day = time[6:8]

    ### Open Netcdf data and read variables ###
    ds_cth_cmsaf = xr.open_dataset(f)

    #adapt cth variable name
    ds_cth_cmsaf = ds_cth_cmsaf.rename({'cth': 'ctth_alti'})
    #print("Updated variables in the dataset:", ds_cth_cmsaf.ctth_alti.values)

    # Assign satellite parameters to ctth_alti variables
    ds_cth_cmsaf['ctth_alti'].attrs['satellite_nominal_latitude'] = ds_cth_cmsaf.subsatellite_lat.values[0]
    ds_cth_cmsaf['ctth_alti'].attrs['satellite_nominal_longitude'] = ds_cth_cmsaf.subsatellite_lon.values[0]
    ds_cth_cmsaf['ctth_alti'].attrs['satellite_nominal_altitude'] = ds_cth_cmsaf.subsatellite_alt.values[0]

    # get output filename
    filename_save = f.split('/')[-1]
    path_output = path_out+'/'+month+'/'+day+'/'

    # Check if the directory exists
    if not os.path.exists(path_output):
        # Create the directory if it doesn't exist
        os.makedirs(path_output)

    # save to new location
    ds_cth_cmsaf.to_netcdf(path_output+filename_save)

        
# %%
if __name__ == "__main__":
    # define years and months to process
    year = 2020
    month = 4
    process_cth_files_of_month(year, month)

    # for whole of 2023
    year = 2023
    months = np.arange(4, 10, 1)

    for month in months:
        process_cth_files_of_month(year, month)

# %%
