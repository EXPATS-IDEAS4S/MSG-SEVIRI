import xarray as xr
from glob import glob
import numpy as np

# Specify the directory containing the NetCDF files
msg_dir = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc/'

# Cloud properties folder
cmsaf_dir = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/'

# Define ouput file
output_file = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/merged_crops.nc'

#msg and cmsaf variables to include in the merged datasets
msg_vars = ['IR_108']
cmsaf_vars = ['cma']

# Get list of crops
list_msg_crops = sorted(glob(msg_dir + '*.nc'))
list_cmsaf_crops = sorted(glob(cmsaf_dir + '*.nc'))

# print length of lists
len_msg = len(list_msg_crops)
len_cmsaf = len(list_cmsaf_crops)

if len_msg == len_msg:

    # Initialize an empty list to store the Datasets
    datasets = []

    # Loop through all NetCDF files in the directory
    for msg_file, cmsaf_file in zip(list_msg_crops, list_cmsaf_crops):
        # Load the MSG and CMSAF NetCDF files
        ds_msg = xr.open_dataset(msg_file)
        ds_cmsaf = xr.open_dataset(cmsaf_file)

        # get lat lon time coordinates
        lat_msg = ds_msg['lat'].values
        lon_msg = ds_msg['lon'].values
        time_msg = ds_msg['time'].values[0]
        #print(lat_msg,lon_msg,time_msg)
        
        lat_cmsaf = ds_cmsaf['lat'].values
        lon_cmsaf = ds_cmsaf['lon'].values
        time_cmsaf = ds_cmsaf['time'].values
        #print(lat_cmsaf,lon_cmsaf,time_cmsaf)
        
        if np.array_equal(lat_cmsaf, lat_msg) and np.array_equal(lon_msg, lon_cmsaf) and time_msg==time_cmsaf:
            # Initialize an empty dataset with the required coordinates and dimensions
            ds_combined = xr.Dataset(
                coords={
                    #'time': time_msg,
                    'x': np.arange(len(lon_msg)),
                    'y': np.arange(len(lat_msg))
                })
            
            # Extract the latitude and longitude coordinates and create a meshgrid
            lat_2d, lon_2d = np.meshgrid(lat_msg, lon_msg, indexing='ij')
            #print(lat_2d, lon_2d)

            # Add lat/lon as variables
            ds_combined['lat'] = (('y', 'x'), lat_2d)
            ds_combined['lon'] = (('y', 'x'), lon_2d)
    
            # Add the required variables from the MSG dataset
            for msg_var in msg_vars:
                if msg_var in ds_msg:
                    ds_combined[msg_var] = (('y', 'x'), ds_msg[msg_var].values.squeeze()) 
                else:
                    print(f"Warning: {cmsaf_var} not found in MSG crop")
                    continue
            
            # Add the cloud mask variables from the CMSAF dataset
            for cmsaf_var in cmsaf_vars:
                if cmsaf_var in ds_cmsaf:
                    ds_combined[cmsaf_var] = (('y', 'x'), ds_cmsaf[cmsaf_var].values.squeeze())
                else:
                    print(f"Warning: {cmsaf_var} not found in CMSAF crop")
                    continue

            # Add a time dimension 
            ds_combined = ds_combined.expand_dims('time')
            ds_combined = ds_combined.assign_coords(time=[time_msg])

            #print(ds_combined)

            # Append the combined dataset to the list
            datasets.append(ds_combined)
        else:
            print('crops coordinates do not match!')
            continue

    # Concatenate all Datasets along the time dimension
    merged_ds = xr.concat(datasets, dim='time')

    # Save the merged dataset to a new NetCDF file
    merged_ds.to_netcdf(output_file)

    print(f"Successfully merged {len(datasets)} files into {output_file}")

else:
    print('something wrong with the lists')

#1242313 nohup