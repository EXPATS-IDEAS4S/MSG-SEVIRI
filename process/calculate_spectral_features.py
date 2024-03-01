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
    ch_108 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_108")
    
    f_names = []
    f_list = []
    
    if not os.path.exists(path_figs+yy+mm+'_BTD_3911_MSG_SEVIRI_EXPATS.nc'):
        print('calculate BTD 3.9-11')
        # read 6.2 micron and 10.8 micron
        ch_039 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_039")
        # calculate feature 1
        f1_3911 = ch_039.IR_039.values - ch_108.IR_108.values    
        f_list.append(f1_3911)
        f_names.append('BTD_3911')
        
           
    if not os.path.exists(path_figs+yy+mm+'_BTD_6211_MSG_SEVIRI_EXPATS.nc'):
        print('calculate BTD 6.2-11')

        # read 6.2 micron and 10.8 micron
        ch_062 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "WV_062")
        # calculate feature 1
        f1_6211 = ch_062.WV_062.values - ch_108.IR_108.values    
        f_list.append(f1_6211)
        f_names.append('BTD_6211')
        
        
    # feature 2: radiance ratio 0.6 micron/1.6 micron
    # higher values expected on ice clouds 
    if not os.path.exists(path_figs+yy+mm+'_RATIO_0616_MSG_SEVIRI_EXPATS.nc'):
        print('calculate RATIO 0.6/1.6')

        ch_006 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "VIS006")
        ch_016 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_016")
        f2_0616 = ch_006.VIS006.values/ch_016.IR_016.values
        f_list.append(f2_0616)
        f_names.append('RATIO_0616')

    # feature 3: BTD 10.8 - 12 micron: indicator of optically thick 
    # cumuliform clouds and optrically thick cirrus
    if not os.path.exists(path_figs+yy+mm+'_BTD_1112_MSG_SEVIRI_EXPATS.nc'):
        print('calculate BTD 11- 12')

        ch_120 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_120")
        f3_1112 = ch_108.IR_108.values - ch_120.IR_120.values
        f_list.append(f3_1112)
        f_names.append('BTD_1112')
      
      
    # feature 4: BTD 8.7 - 10.8 large positive for cirrus clouds and lower over water clouds
    if not os.path.exists(path_figs+yy+mm+'_BTD_8711_MSG_SEVIRI_EXPATS.nc'):
        print('calculate BTD 8.7-11')

        ch_087 = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_087")
        f4_8711 =  ch_087.IR_087.values - ch_108.IR_108.values 
        f_list.append(f4_8711)
        f_names.append('BTD_8711')

    print(f_names)
    print('storing in ncdfs')
    # saving features to ncdf
    for i, ch in enumerate(f_list):
        
        # read var name
        f_name = f_names[i]
        
        # store features in ncdf array
        dataset_feature = xr.Dataset(
        data_vars={
            "feature": (('time','x', 'y'), ch, {'long_name':f_name})},
        coords={
            "time": (('time',), ch_108['time'].values, {"axis": "T","standard_name": "time"}), # leave units intentionally blank, to be defined in the encoding
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
        