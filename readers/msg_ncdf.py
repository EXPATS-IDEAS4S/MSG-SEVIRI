"""
Code to read msg files in ncdf format converted using satpy
"""
    
    
    
from readers.files_dirs import filelist_ncdf
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
    print(len(data_sel['lon grid'].values[:,0 ]))
    print(len(data_sel['lat grid'].values[0, :]))

    data['lat_grid'] = (('x'), data_sel['lon grid'].values[0,:])
    data['lon_grid'] = (('y'), data_sel['lat grid'].values[:,0])
    data = data.drop_vars('lon grid')
    data = data.drop_vars('lat grid')
    return data