"""
Code to build folder structure and copy ncdf files after merging them in the right folder
"""

from readers.files_dirs import path_ncdf, filelist_ncdf, path_dir_tree
from readers.msg_ncdf import read_ncdf_day
import numpy as np
import os
import glob
import logging

def main():
    
    # Basic configuration of logging for incomplete day lists of files
    logging.basicConfig(level=logging.INFO, 
                        filename=path_dir_tree+'incomplete_days_list.log', 
                        filemode='w',
                        format='%(asctime)s - %(levelname)s - %(message)s')

    # read dates from filelist and create daily files
    dates = read_dates(filelist_ncdf)

    print(dates)
    
    for date in dates:
        
        print('processing '+date)
        
        # read year, month, day
        yy, mm, dd = extract_yymmdd(date)

        # Check if the output directory exists otherwise create it
        if not os.path.exists(path_dir_tree+yy):
            os.makedirs(path_dir_tree+yy)
        elif not os.path.exists(path_dir_tree+yy+'/'+mm+'/'):
            os.makedirs(path_dir_tree+'/'+yy+'/'+mm)
        
        path_ncdf_out = path_dir_tree+yy+'/'+mm+'/'
        print(date)
        
        
        # if daily file does not already exist, process file list
        if not os.path.exists(path_ncdf_out+date+'_MSG_SEVIRI_EXPATS.nc'):
            
            # if file list is complete (96 files, one every 15 mins) process
            if len(np.sort(glob.glob(path_ncdf+'*'+date+'*'))) == 96:
                
                # select and merge all files of the date
                data, files_to_delete = read_ncdf_day(date)

                # compress and store ncdf of the day in the folder structure
                compress_and_store(data, date, path_ncdf_out)
                
                # removing files of stored data if ncdf is correctly produced
                if os.path.exists(path_ncdf_out+date+'_MSG_SEVIRI_EXPATS.nc'):
                    
                    # delete files of the list
                    [os.remove(filename) for filename in files_to_delete]
                
                                
            else:
                # writing date name in the log of incomplete files 
                logging.info(f"'{date}' incomplete: {len(np.sort(glob.glob(path_ncdf+'*'+date+'*')))} files")



def compress_and_store(data, date, path):
    """
    function to store daily files in specific folder

    Args:
        data (_type_): _description_
        path (_type_): _description_
    """
    data.to_netcdf(path+date+'_MSG_SEVIRI_EXPATS.nc', \
        encoding={'IR_016':{"zlib":True, "complevel":9},\
                'IR_039':{"zlib":True, "complevel":9},\
                'IR_087':{"zlib":True, "complevel":9},\
                'IR_097':{"zlib":True, "complevel":9},\
                'IR_108':{"zlib":True, "complevel":9},\
                'IR_120':{"zlib":True, "complevel":9},\
                'IR_134':{"zlib":True, "complevel":9},\
                'VIS006':{"zlib":True, "complevel":9},\
                'VIS008':{"zlib":True, "complevel":9},\
                'WV_062':{"zlib":True, "complevel":9},\
                'WV_073':{"zlib":True, "complevel":9},\
                'time':{"units": "seconds since 2020-01-01", "dtype": "i4"}})


  
def extract_yymmdd(date):
    """
    Extract yy mm and day from the given date
    Args:
        date (_type_): _description_
    """
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    return yy, mm, dd


def read_dates(filelist_ncdf):
    """
    function to extract dates from filenames

    Args:
        filelist_ncdf (list of strings): list containing all filenames
    """
    print(filelist_ncdf)
    
    # number of characters before the date
    len_path = len(path_ncdf)
    start = len('MSG3-SEVI-MSG15-0100-NA-')
    string_len = len('20230711')
    dates_all = [file[len_path+start:len_path+start+string_len] for file in filelist_ncdf]
    dates = np.asarray(dates_all)
    
    return np.unique(dates)

if __name__ == "__main__":
    main()
    