"""
code to derive spectral features useful for detecting deep convection
and precipitation, based on master thesis of Claudia

"""
from readers.msg_ncdf import read_ncdf, ch_list, ch_max_list, ch_min_list
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
    ch_062 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "WV_062")
    ch_108 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_108")
    
    # calculate feature 1
    f1_6211 = ch_062.WV_062.values - ch_108.IR_108.values    
    
    # feature 2: radiance ratio 0.6 micron/1.6 micron
    # higher values expected on ice clouds 
    ch_006 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "VIS006")
    ch_016 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_016")
    
    f2_0616 = ch_006.VIS006.values/ch_016.IR_016.values
    
    # feature 3: BTD 10.8 - 12 micron: indicator of optically thick 
    # cumuliform clouds and optrically thick cirrus 
    ch_120 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_120")
    
    f3_1112 = ch_108.IR_108.values - ch_120.IR_120.values
    
    # feature 4: BTD 8.7 - 10.8 large positive for cirrus clouds and lower over water clouds
    ch_087 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_087")

    f4_8711 =  ch_087.IR_087.values - ch_108.IR_108.values 
    
    # store features in ncdf array
    dataset_features = xr.Dataset(
        data_vars={
            "feature_1": (('time','x', 'y'), f1_6211, {'long_name': 'BTD 6.2-10.8', 'units':'K', "standard_name": "BTD 6.2 - 11 micron for deep convective cloud detection "}),
            'feature_2':(('time','x', 'y'), f2_0616, {'long_name': 'radiance ratio 0.6/1.6', 'units':'', "standard_name": "radiance ratio 0.6 micron/1.6 micron"}),
            'feature_3': (('time','x', 'y'), f3_1112, {'long_name': 'BTD 10.8 - 12 micron', 'units':'K', "standard_name": "BTD 10.8 - 12 micron"}),
            'feature_4':(('time','x', 'y'), f4_8711, {'long_name': 'BTD 8.7 - 10.8', 'units':'K', "standard_name": "BTD 8.7 - 10.8"}),
        },
        coords={
            "time": (('time',), ch_087['time'].values, {"axis": "T","standard_name": "time"}), # leave units intentionally blank, to be defined in the encoding
        },
    )
    
    # saving features to ncdf
    compress_and_store(dataset_features, '202307', path_figs)



def compress_and_store(data, date, path):
    """
    function to store daily files in specific folder

    Args:
        data (_type_): _description_
        path (_type_): _description_
    """
    data.to_netcdf(path+date+'FEATURES_MSG_SEVIRI_EXPATS.nc', \
        encoding={'feature_1':{"zlib":True, "complevel":9},\
                'feature_2':{"zlib":True, "complevel":9},\
                'feature_3':{"zlib":True, "complevel":9},\
                'feature_4':{"zlib":True, "complevel":9},\
                'time':{"units": "seconds since 2020-01-01", "dtype": "i4"}})

    return



if __name__ == "__main__":
    main()
        