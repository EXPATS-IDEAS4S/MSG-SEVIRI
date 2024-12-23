"""
Match Cloud products from CM SAF to MSG regular grid

@author: Daniele Corradini
"""
import numpy as np
import os
import sys
from glob import glob
import xarray as xr

#import own methods
sys.path.append('/home/dcorradi/Documents/Codes/MSG-SEVIRI/')
from process.regrid_functions import regrid_data, generate_regular_grid

#Year of data
years = ['2013', '2014']
variable_names = ['cma', 'quality', 'status_flag', 'conditions']

# Define extent of domain of interest
lonmax, lonmin, latmax, latmin = 16., 5., 51.5, 42.
#extent = [lon_min, lon_max, lat_min, lat_max] #[left, right, bottom ,top]

# Create reg lat/lon data
lat_points, lon_points = generate_regular_grid(latmin,latmax,lonmin,lonmax,0.04)
msg_lat_grid, msg_lon_grid = np.meshgrid(lat_points,lon_points,indexing='ij')
#print(np.shape(msg_lat_grid))

def get_cmsaf_lat_lon(ds_cmsaf, ds_aux):
        # Get lat lon from AUX file
        grid_idx = ds_cmsaf.georef_offset_corrected.values
        lat_aux = ds_aux['lat'].values[grid_idx]
        #print('lat aux', lat_aux)
        lon_aux = ds_aux['lon'].values[grid_idx]
        #print('lon aux', lon_aux)
        return  lat_aux, lon_aux

for year in years:
    # Define the folder of the CMSAF file to regrid
    cmsaf_folder = "/data/sat/msg/CM_SAF/CMA/"+year+"/*/*/"
    cmsaf_filepattern = "CMAin*.nc"
    cmsaf_aux_path = "/data/sat/msg/CM_SAF/CMA/"+year+"/CM_SAF_CLAAS3_L2_AUX.nc"
    
    # Define path for saving the processed CM SAF file
    output_folder = "/data/sat/msg/CM_SAF/CMA_processed/"+year+"/"

    # Open all CMSAF files
    cmsaf_files = sorted(glob(cmsaf_folder+cmsaf_filepattern))

    # open dataset for aux file
    ds_aux = xr.open_dataset(cmsaf_aux_path, decode_times=False)
    #print(ds_aux.lon.values)

    # Loop through each cmsaf file
    for cmsaf_file in cmsaf_files:
        # Open dataset for CMSAF
        ds_cmsaf = xr.open_dataset(cmsaf_file)

        # Extract time and date
        time = ds_cmsaf.time.values[0]
        print(time)

        # Extract month, and day
        month = str(time).split('-')[1]
        day = str(time).split('-')[2][0:2]

        # Get the lat/lon from auxiliary file
        lat_aux, lon_aux = get_cmsaf_lat_lon(ds_cmsaf, ds_aux)

        # Create an empty xarray Dataset for regridded data
        ds_regridded = xr.Dataset()

        # Loop through the variables to regrid
        for var_name in variable_names:  # Add all variable names here
            if var_name in ds_cmsaf.variables:
                print(f"Regridding variable: {var_name}")
                
                # Extract variable data
                var_data = ds_cmsaf[var_name].values[0, :, :]
                
                # Regrid the data
                regridded_data = regrid_data(lat_aux, lon_aux, var_data, msg_lat_grid, msg_lon_grid, 'nearest')
                
                # Create a DataArray for the regridded data
                regridded_da = xr.DataArray(
                    regridded_data,
                    dims=("lat", "lon"),
                    coords={"lat": lat_points, "lon": lon_points},
                    name=var_name
                )
                
                # Add the regridded DataArray to the regridded dataset
                ds_regridded[var_name] = regridded_da

        # Add a new dimension for the time coordinate
        ds_regridded = ds_regridded.expand_dims('time', axis=0)
        ds_regridded['time'] = [time]

        # Define the output path and save the regridded data
        out_path = output_folder + month + '/' + day + '/'
        if not os.path.exists(out_path):
            os.makedirs(out_path)
        save_filename = os.path.join(out_path, os.path.basename(cmsaf_file))
        ds_regridded.to_netcdf(save_filename)
        print('Product saved to', save_filename, '\n')
        

"""
# Loop through each cmsaf file
for cmsaf_file in cmsaf_files:
    #open dataset for cmsaf
    ds_cmsaf = xr.open_dataset(cmsaf_file)

    #extract time and date
    time = ds_cmsaf.time.values[0]
    print(time)

    # Extract month, and day
    month = str(time).split('-')[1]
    day = str(time).split('-')[2][0:2]
    #print(month,day)

    #get the lat lon from auxilary 
    lat_aux, lon_aux = get_cmsaf_lat_lon(ds_cmsaf, ds_aux)

    # Regrid the data
    cmsaf_data = ds_cmsaf['cma'].values[0,:,:]
    
    regridded_data = regrid_data(lat_aux, lon_aux, cmsaf_data, msg_lat_grid, msg_lon_grid, 'nearest')
    #print(np.shape(regridded_data))
    
    #create an empty xarray Dataset 
    ds = xr.Dataset()

    cmsaf_da = xr.DataArray(
        regridded_data,
        dims=("y", "x"),
        coords={"lat": ("y", lat_points), "lon": ("x", lon_points)},
        name=cmsaf_name)
  
    # combine DataArrays of rain rate into xarray object
    ds[cmsaf_name] = cmsaf_da
    
    # Add a new dimension for the start time coordinate
    ds = ds.expand_dims('time', axis=0)
    ds['time'] = [time]

    #print(ds)
    
    out_path = output_folder+month+'/'+day+'/'

    # Check if the directory exists
    if not os.path.exists(out_path):
            # Create the directory if it doesn't exist
            os.makedirs(out_path)

    # Define a new filename for saving regridded data
    save_filename = os.path.join(out_path, os.path.basename(cmsaf_file))

    # Save in netCDF format
    ds.to_netcdf(save_filename)
    print('product saved to', save_filename,'\n')
    #exit()
"""