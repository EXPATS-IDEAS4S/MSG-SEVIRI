import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import pyproj
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from datetime import datetime
from glob import glob
import matplotlib.cm as cm
import matplotlib.colors as colors
from scipy.interpolate import griddata
import xarray as xr
import os
import pandas as pd

#import methods
from process_cth_functions import insert_time_attr, insert_satellite_id, insert_subsatellite_pos_attr, insert_gdal_projection, insert_lat_lon

### Define Paths ###

#path where cth data are stored
path_to_files = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/CM_SAF/'

#Path output
path_out = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/CM_SAF/CTH_process/'

#path to save the images
path_fig = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/Fig/CTH_maps/test/'

#path to nwc saf file
path_nwc = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/NWC_SAF/'
nc_file_nwc = 'S_NWC_CTTH_*.nc'

#open all files in directory 
nc_file = "CTX*.nc" #'CTXin20210712000000405SVMSGI1UD.nc'
fnames = sorted(glob(path_to_files+nc_file))
#print(fnames)

#AUx data
aux_file = 'CM_SAF_CLAAS3_L2_AUX.nc'

ds_aux = xr.open_dataset(path_to_files+aux_file, decode_times=False)
print(ds_aux)
print(np.shape(ds_aux.lat.values))
print(np.shape(ds_aux.lon.values))



#Read and process CTH data at different temporal steps 
for t,f in enumerate(fnames):
    print(f)
    ### Open Netcdf data and read variables ###
    ds_cth_cmsaf = xr.open_dataset(f)

    #insert time in the global attributes
    print('time in the variables')
    print(ds_cth_cmsaf.time.values)
    ds_cth_cmsaf = insert_time_attr(ds_cth_cmsaf)
    print("\nUpdated Dataset with New Global Attribute:")
    print(ds_cth_cmsaf.nominal_product_time)

    # add satellite identifier in the global attributes
    print(ds_cth_cmsaf.platform_flag.values)
    ds_cth_cmsaf = insert_satellite_id(ds_cth_cmsaf)
    print(ds_cth_cmsaf.satellite_identifier)

    # Add subsatellite lon in the global attrs
    print(ds_cth_cmsaf.subsatellite_lon.values)
    ds_cth_cmsaf = insert_subsatellite_pos_attr(ds_cth_cmsaf)
    print(ds_cth_cmsaf.attrs['sub-satellite_longitude'])

    #insert projection info in attrs
    print(ds_cth_cmsaf.projection)
    ds_cth_cmsaf = insert_gdal_projection(ds_cth_cmsaf)
    print(ds_cth_cmsaf.attrs['gdal projection'])

    #adapt cth variable name
    ds_cth_cmsaf = ds_cth_cmsaf.rename({'cth': 'ctth_alti'})
    print("Updated variables in the dataset:", ds_cth_cmsaf.ctth_alti.values)

    # insert lat lon coordinates from aux file
    ds_cth_cmsaf = insert_lat_lon(ds_cth_cmsaf,ds_aux)
    print(ds_cth_cmsaf.lat, ds_cth_cmsaf.lon)

    filename_save = f.split('/')[-1]

    ds_cth_cmsaf.to_netcdf(path_out+filename_save)
    print(f'\nfile {filename_save} is saved')

    exit()
   



    
