"""
Processing CTH data from CMSAF to make it compatible to Satpy for the parallax correction

@author: Daniele Corradini
"""

from glob import glob
import xarray as xr
import os

### Define Paths ###

year = '2018'

#path where cth data are stored
path_to_files = '/data/sat/msg/CM_SAF/CTH/'+year+'/0*/*/'

#Path output
path_out = '/data/sat/msg/CM_SAF/CTH_processed/'+year+'/' 

#open all files in directory 
nc_file = "CTX*.nc" #'CTXin20210712000000405SVMSGI1UD.nc'
fnames = sorted(glob(path_to_files+nc_file))
#print(fnames)

#Read and process CTH data at different temporal steps 
for t,f in enumerate(fnames):
    print(f.split('/')[-1])

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

    #print(ds_cth_cmsaf['ctth_alti'].attrs)

    filename_save = f.split('/')[-1]

    path_output = path_out+'/'+month+'/'+day+'/'

    # Check if the directory exists
    if not os.path.exists(path_output):
        # Create the directory if it doesn't exist
        os.makedirs(path_output)

    ds_cth_cmsaf.to_netcdf(path_output+filename_save)
    print(f'\nfile {filename_save} is saved')

    #exit()
    



        




    
