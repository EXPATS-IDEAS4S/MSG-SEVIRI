

from readers.msg_ncdf import read_ncdf
from readers.files_dirs import path_dir_tree, path_figs
import numpy as np
import matplotlib.pyplot as plt
import os
import xarray as xr
import glob
import shutil


path_incoming = '/data/sat/msg/incoming/'

file_list = np.sort(glob.glob(path_incoming+'*.nat'))
len_path = len(path_incoming)
# MSG3-SEVI-MSG15-0100-NA-20230404225741.553000000Z-NA
len_str_before = len('MSG3-SEVI-MSG15-0100-NA-')
N = len('20230404')

dates = [file[len_str_before+len_path:len_str_before+len_path+N] for file in file_list]

for date in dates:
    
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    
    print('moving day', date)
    
    # create folder for the selected day if it does not exist
    os.makedirs('/data/sat/msg/nat/'+yy+'/'+mm+'/'+dd+'/', exist_ok=True) 
    
    # list of files to move
    files_day = np.sort(glob.glob(path_incoming+'MSG3-SEVI-MSG15-0100-NA-'+date+'*.nat'))
    
    # moving all files in the day folder
    [shutil.move(file_day, '/data/sat/msg/nat/'+yy+'/'+mm+'/'+dd+'/') for file_day in files_day]
    
