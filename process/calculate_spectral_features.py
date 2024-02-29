"""
code to derive spectral features useful for detecting deep convection
and precipitation, based on master thesis of Claudia

"""
from readers.msg_ncdf import read_ncdf
from readers.files_dirs import path_dir_tree, path_figs
import numpy as np
import matplotlib.pyplot as plt
import os
import xarray as xr

def main():

    # read data of the month of july
    yy = '2023'
    mm = '07'
    
    # feature 1: BTD 6.2 - 11 micron for deep convective cloud detection 
    # BTD > 0 --> convective areas
    
    # read 6.2 micron and 10.8 micron
    #ch_062 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "WV_062")
    #ch_108 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_108")
    
    # calculate feature 1
    #f1_6211 = ch_062.WV_062.values - ch_108.IR_108.values    
    
    # feature 2: radiance ratio 0.6 micron/1.6 micron
    # higher values expected on ice clouds 
    ch_006 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "VIS006")
    ch_016 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_016")
    print(np.min(ch_006.VIS006.values), np.min(ch_006.VIS006.values))
    print(np.max(ch_016.IR_016.values), np.max(ch_016.IR_016.values))

    f2_0616 = ch_006.VIS006.values/ch_016.IR_016.values
    
    # feature 3: BTD 10.8 - 12 micron: indicator of optically thick 
    # cumuliform clouds and optrically thick cirrus 
    #ch_120 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_120")
    
    #f3_1112 = ch_108.IR_108.values - ch_120.IR_120.values
    
    # feature 4: BTD 8.7 - 10.8 large positive for cirrus clouds and lower over water clouds
    #ch_087 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_087")

    #f4_8711 =  ch_087.IR_087.values - ch_108.IR_108.values 
    
   
    
    # saving features to ncdf
    f_list = [f1_6211, f2_0616, f3_1112, f4_8711]
    #f_names = ['BTD_6211', 'RATIO_0616', 'BTD_1112', 'BTD_8711']
    for i, ch in enumerate(f_list):
        
        # read var name
        f_name = f_names[i]
        
        # store features in ncdf array
        dataset_feature = xr.Dataset(
        data_vars={
            "feature": (('time','x', 'y'), ch, {'long_name':f_name})},
        coords={
            "time": (('time',), ch_087['time'].values, {"axis": "T","standard_name": "time"}), # leave units intentionally blank, to be defined in the encoding
        },)
        
        compress_and_store(dataset_feature, f_name, '202307', path_figs)



def compress_and_store(data, name, date, path):
    """
    function to store daily files in specific folder

    Args:
        data (xarray dataset): dataset containing data to store
        path (_type_): path where ncdf files are stored
    """
    data.to_netcdf(path+date+'_'+name+'_MSG_SEVIRI_EXPATS.nc', \
        encoding={'feature':{"zlib":True, "complevel":9},\
                'time':{"units": "seconds since 2020-01-01", "dtype": "i4"}})

    return



if __name__ == "__main__":
    main()
        