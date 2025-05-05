"""
reading routines for CM SAF data
Returns:
    _type_: _description_
"""

import xarray as xr
import numpy as np
import glob
from datetime import datetime



def read_CM_SAF(path_to_files):
    
    """
    function to read ncdf list of cloud mask files from cm saf 
    """

    print(path_to_files)
    # listing files to be read
    filelist = sorted(glob.glob(path_to_files+'*UD.nc'))
    
    # read dataset
    data = xr.open_mfdataset(filelist)
    
    #data_sel = data.isel(end_time=0)

    # removing time dimension from lat and lons
    #data['lat'] = (('y','x'), data_sel['lon'].values)
    #data['lon'] = (('y','x'), data_sel['lat'].values)
    #data = data.drop_vars('lon')
    #data = data.drop_vars('lat')
    
    return data

def read_lat_lon_CMSAF(CM_SAF_path):
    """
    read lat lon file of CMsaf dataset
    
    Args:
        CM_SAF_path (string): path to cmsaf files
    """

    data = xr.open_dataset(CM_SAF_path+'CM_SAF_CLAAS3_L2_AUX.nc', decode_times=False)
    
    # selecting data with georeference offset corrected ( == 1 UB)
    lat = data.lat.values[1,:,:]
    lon = data.lon.values[1,:,:]

    return(lat, lon)