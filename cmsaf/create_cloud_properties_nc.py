import numpy as np
import os
import xarray as xr
from glob import glob
import pandas as pd
import sys

#import own methods
sys.path.append('/home/dcorradi/Documents/Codes/MSG-SEVIRI/')
from process.regrid_functions import regrid_data, generate_regular_grid
#from cmsaf.regrid_cmsaf import get_cmsaf_lat_lon

def get_cmsaf_lat_lon(ds_cmsaf, ds_aux):
    # Get lat lon from AUX file
    grid_idx = ds_cmsaf.georef_offset_corrected.values
    lat_aux = ds_aux['lat'].values[grid_idx]
    #print('lat aux', lat_aux)
    lon_aux = ds_aux['lon'].values[grid_idx]
    #print('lon aux', lon_aux)
    return  lat_aux[0,:,:], lon_aux[0,:,:]

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
    #save the features using a similar name of the HDF5 file but in netCDF format
    #ds.to_netcdf(proj_file_path+filename_save)
    ds.to_netcdf(proj_file_path+filename_save, \
        encoding={'cot':{"zlib":True, "complevel":9},\
                'cph':{"zlib":True, "complevel":9},\
                'cwp':{"zlib":True, "complevel":9},\
                'cre':{"zlib":True, "complevel":9},\
                'ctt':{"zlib":True, "complevel":9},\
                'ctp':{"zlib":True, "complevel":9},\
                'cth':{"zlib":True, "complevel":9},\
                'cma':{"zlib":True, "complevel":9},\
                'time':{"units": "seconds since 2000-01-01", "dtype": "i4"}})
    print(f'{filename} product saved in {proj_file_path}\n')

#define year and month of data
year = '2013'
months = ['04','05', '06', '07', '08', '09']

# Define extent of domain of interest
lon_max, lon_min, lat_max, lat_min = 16.0, 5.0, 51.5, 42.0
grid_size = 0.04

#open dataset with aux info 
cmsaf_aux_path = "/data/sat/msg/CM_SAF/CM_SAF_CLAAS3_L2_AUX.nc"
ds_aux = xr.open_dataset(cmsaf_aux_path,decode_times=False)
#print(ds_aux) #TODO how to do in case the crop is wrong?

#Define name of variables
variable_mapping = {
    "CPP": ["cot", "cph", "cwp", "cre"], #cloud optical thickness, cloud phase, cloud water path, cloud effective radius
    "CTX": ["ctt", "ctp", "cth"], #cloud top temperature, cloud top pressure, cloud top height
    "CMA": ["cma"]                #cloud mask
}

#find regular grid
lat_points, lon_points = generate_regular_grid(lat_min, lat_max, lon_min, lon_max, grid_size)
msg_lat_grid, msg_lon_grid = np.meshgrid(lat_points, lon_points, indexing='ij')
print(msg_lat_grid.shape)
#print(msg_lon_grid)

for month in months:

    # Paths and parameters
    cmsaf_path = '/data/sat/msg/CM_SAF/'
    cpp_folder = f'{cmsaf_path}CPP/{year}/{month}'
    ctx_folder =  f'{cmsaf_path}CTX/{year}/{month}'
    cma_folder =  f'{cmsaf_path}CMA/{year}/{month}'    

    #output folder, create if don't exist
    output_folder =f'{cmsaf_path}merged_cloud_properties/{year}/{month}/'
    if not os.path.exists(output_folder):
        # Create the directory if it doesn't exist
        os.makedirs(output_folder) 

    # Collect all file paths
    cpp_files = sorted(glob(cpp_folder+ "/*/*.nc"))
    ctx_files = sorted(glob(ctx_folder+ "/*/*.nc"))
    cma_files = sorted(glob(cma_folder+ "/*/*.nc"))
    print(len(cpp_files),len(ctx_files),len(cma_files))


    if len(cpp_files) == len(ctx_files) and len(cma_files) == len(cpp_files):

        # Create a DataFrame with the file paths
        df_file_groups = pd.DataFrame({
            "CPP": cpp_files,
            "CTX": ctx_files,
            "CMA": cma_files
        })

        #print(df_file_groups)

        # Process each timestamp
        n_files = len(cpp_files)

        # initialize day variable
        last_day = 0
        #count = 0

        for t in range(n_files):
            ds_time = xr.open_dataset(cpp_files[t])
            #get timestamp
            timestamp = ds_time.time.values[0]
            print(timestamp)

            #extract day from time string
            day = pd.to_datetime(timestamp).day
            month =  pd.to_datetime(timestamp).month
            year =  pd.to_datetime(timestamp).year 

            #get lat lon
            lat_aux, lon_aux = get_cmsaf_lat_lon(ds_time, ds_aux)
            #print(lat_aux.shape)
            #print(lon_aux.shape)

            #initialize list of dataset to merge
            datasets = []

            #loop over the different file type
            for key in df_file_groups.columns.tolist():
                    #for each file type, open the correspondent dataset for the current timestamp
                    ds = xr.open_dataset(df_file_groups.loc[t,key])
                    #print(ds)
                    #merge only the dataarry containig the relevant variables inside each dataset
                    for var in variable_mapping[key]:
                        if var in ds:
                            datasets.append(ds[var])
            #print(datasets)
            
            if datasets:
                merged_ds = xr.merge(datasets)
                #print(merged_ds)

                # Regrid each variable in the merged dataset
                regridded_data = {}
                for var in merged_ds:
                    #print(var)
                    data = merged_ds[var].values[0,:,:]
                    #print(np.sum(np.isnan(data)) / (data.shape[0]*data.shape[1]))
                    
                    regridded_data[var] = regrid_data(lat_aux, lon_aux, data, msg_lat_grid, msg_lon_grid, 'nearest')
                    #print(np.sum(np.isnan(regridded_data[var])) / (msg_lat_grid.shape[0]*msg_lat_grid.shape[1]))
                #print(regridded_data)

                # Create an xarray Dataset
                regridded_ds = xr.Dataset()
                for var, data in regridded_data.items():
                    regridded_ds[var] = xr.DataArray(data, dims=("lat", "lon"), coords={"lat": lat_points, "lon": lon_points})

                
                regridded_ds = regridded_ds.expand_dims('time', axis=0)
                #regridded_ds['time'] = pd.to_datetime([timestamp], format='%Y%m%d%H%M%S')
                regridded_ds['time'] = merged_ds['time']
                #print(regridded_ds)

                if day == last_day:
                    ds_day = xr.concat([ds_day, regridded_ds], dim='time')

                    #deal with the last timestep
                    if t==n_files-1:
                        filename = f"MCP_{year:04d}-{month:02d}-{day:02d}_regrid.nc"
                        compress_and_save(ds_day,output_folder,filename)
                else:
                    if t>0:
                        #save the daily dataset 
                        filename = f"MCP_{year:04d}-{month:02d}-{day-1:02d}_regrid.nc"
                        compress_and_save(ds_day,output_folder,filename)
                        #update dataset with the next day
                    ds_day = regridded_ds
                #count+=1

                last_day = day
                #print(ds_day) 

        print(f'Processing concluded for month {month}!')
    else:
        print('something wrong with the number of files')
        exit()

#920961 nohup