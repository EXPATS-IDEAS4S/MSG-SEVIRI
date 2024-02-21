"""
Code to read msg files in ncdf format converted using satpy
"""
    
    
    
from readers.files_dirs import filelist_ncdf, orography_file
import xarray as xr
    


DROP_VARIABLES = [
    "WV_062",
    "WV_073",
    "VIS008",
    "VIS006",
    "IR_097",
    "IR_016",
    "IR_087",
    "IR_039",
    "IR_134",
    "IR_016",
    "IR_120",
]


def read_ncdf():
    
    """
    function to read ncdf list 
    
    """
    
    data = xr.open_mfdataset(filelist_ncdf, drop_variables=DROP_VARIABLES)
    
    data_sel = data.isel(end_time=0)

    # removing time dimension from lat and lons
    data['lat'] = (('y','x'), data_sel['lon'].values)
    data['lon'] = (('y','x'), data_sel['lat'].values)
    #data = data.drop_vars('lon')
    #data = data.drop_vars('lat')
    
    return data


def read_orography():
    
    data = xr.open_dataset(orography_file)
    return data
    