

from readers.msg_ncdf import read_ncdf
from readers.files_dirs import path_dir_tree, path_figs
import numpy as np
import matplotlib.pyplot as plt
import os
import xarray as xr
import glob
import shutil

# select file type to process
files = 'cth_cmsaf'

if files == "msg":
    path_incoming = '/data/sat/msg/incoming/'
    path_destination = '/data/sat/msg/nat/'
    file_list = np.sort(glob.glob(path_incoming+'*.nat'))
    len_path = len(path_incoming)
    # MSG3-SEVI-MSG15-0100-NA-20230404225741.553000000Z-NA
    len_str_before = len('MSG3-SEVI-MSG15-0100-NA-')
    N = len('20230404')
    dates = [file[len_str_before+len_path:len_str_before+len_path+N] for file in file_list]
    
    
elif files == "cth_cmsaf":
    # find name of dir of the folder of downloaded files
    import os
    path_incoming = '/data/sat/msg/CM_SAF/' # list of subdirectories and files    
    path_destination = '/data/sat/msg/CM_SAF/'
    file_list = np.sort(glob.glob(path_incoming+'*.nc'))
    len_path = len(path_incoming)
    len_str_before = len('CTXin')
    N = len('20230404')
    dates = [file[len_str_before+len_path:len_str_before+len_path+N] for file in file_list]
    print(dates)

# loop on all dates to move files in the right folder
for date in dates:
    
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    
    print('moving day', date)
    
    # create folder for the selected day if it does not exist
    os.makedirs(path_destination+yy+'/'+mm+'/'+dd+'/', exist_ok=True) 
    
    # list of files to move
    if files == "msg":
        files_day = np.sort(glob.glob(path_incoming+'MSG3-SEVI-MSG15-0100-NA-'+date+'*.nat'))
    elif files == "cth_cmsaf":
        files_day = np.sort(glob.glob(path_incoming+'CTXin'+date+'*.nc'))

    # moving all files in the day folder
    [shutil.move(file_day, path_destination+yy+'/'+mm+'/'+dd+'/') for file_day in files_day]
    
