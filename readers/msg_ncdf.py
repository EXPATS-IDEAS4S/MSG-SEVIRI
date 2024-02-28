"""
Code to read msg files in ncdf format converted using satpy
"""
    
    
    
from readers.files_dirs import filelist_ncdf, orography_file, path_ncdf
import xarray as xr
import numpy as np
import glob

# list of channel name strings 
ch_list = ['IR_108', 'IR_039', 'IR_016', 'IR_087', 'IR_097', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']


DROP_VARIABLES = [
    "IR_108",
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


def read_ncdf(path_to_files, var_to_read):
    
    """
    function to read ncdf list 
    """
    # create a list of the channel to read
    list_to_read = [var_to_read]
    
    # get all elements of DROP_VARIABLES not in list_to_read
    l3 = [x for x in DROP_VARIABLES if x not in list_to_read]
    
    # listing files to be read
    filelist = sorted(glob.glob(path_to_files+'*.nc'))
    
    # read dataset
    data = xr.open_mfdataset(filelist, drop_variables=l3)
    
    #data_sel = data.isel(end_time=0)

    # removing time dimension from lat and lons
    #data['lat'] = (('y','x'), data_sel['lon'].values)
    #data['lon'] = (('y','x'), data_sel['lat'].values)
    #data = data.drop_vars('lon')
    #data = data.drop_vars('lat')
    
    return data


def read_orography():
    
    data = xr.open_dataset(orography_file)
    return data
    
    
def read_ncdf_day(date):
    """
    reads all files of a day and after merging, deletes the ncdf 

    Args:
        date (string): selected date

    Returns:
        data: xarray dataset of merged single files for the day
    """
    # read filelist of files belonging to the same day
    filelist = np.sort(glob.glob(path_ncdf+'*'+date+'*'))

    print("number of files", len(filelist))
    data = xr.open_mfdataset(filelist)
    data = data.chunk({'end_time': len(data.end_time)})
    data = data.rename({'end_time':'time'})

    
    return data, filelist



def read_dates(filelist_ncdf):
    """
    function to extract dates from filenames

    Args:
        filelist_ncdf (list of strings): list containing all filenames
    """    
    # number of characters before the date
    len_path = len(path_ncdf)
    start = len('MSG3-SEVI-MSG15-0100-NA-')
    string_len = len('20230711')
    dates_all = [file[len_path+start:len_path+start+string_len] for file in filelist_ncdf]
    dates = np.asarray(dates_all)
    
    return np.unique(dates)



def read_lat_lon_file():
    """
    read lat lon file and give as output the lats lons 
    """
    
    data = xr.open_dataset('/data/sat/msg/lat_lon_grid.nc')
    
    return data.lon.values, data.lat.values