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
year = '2023'

# Define the folder of the CMSAF file to regrid
cmsaf_folder = "/data/sat/msg/CM_SAF/CMA/"+year+"/*/*/"
cmsaf_filepattern = "CMAin*405SVMSGI1UD.nc"
cmsaf_aux_path = "/data/sat/msg/CM_SAF/CMA/"+year+"/CM_SAF_CLAAS3_L2_AUX.nc"
cmsaf_name = 'cma'

# Define path for saving the processed CM SAF file
output_folder = "/data/sat/msg/CM_SAF/CMA_processed/"+year+"/"

# Define extent of domain of interest
lonmax, lonmin, latmax, latmin = 16., 5., 51.5, 42.
#extent = [lon_min, lon_max, lat_min, lat_max] #[left, right, bottom ,top]

# Create reg lat/lon data
lat_points, lon_points = generate_regular_grid(latmin,latmax,lonmin,lonmax,0.04)
msg_lat_grid, msg_lon_grid = np.meshgrid(lat_points,lon_points,indexing='ij')
#print(np.shape(msg_lat_grid))

# Open all CMSAF files
cmsaf_files = sorted(glob(cmsaf_folder+cmsaf_filepattern))

# open dataset for aux file
ds_aux = xr.open_dataset(cmsaf_aux_path, decode_times=False)
#print(ds_aux.lon.values)

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

    # Get lat lon from AUX file
    grid_idx = ds_cmsaf.georef_offset_corrected.values
    lat_aux = ds_aux['lat'].values[grid_idx]
    #print('lat aux', lat_aux)
    lon_aux = ds_aux['lon'].values[grid_idx]
    #print('lon aux', lon_aux)

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
