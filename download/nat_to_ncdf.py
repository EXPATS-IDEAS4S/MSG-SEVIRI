"""
Open MSG-SEVIRI nat files fully disk with Satpy 
Crop it to area of interest, project it in latlon grid and convert it to netCDF

author: Daniele Corradini
last Edit: December 2023
"""

##################
#import libraries#
##################

import satpy 
from glob import glob
import xarray as xr
import datetime
import os
import numpy as np
import time

# Start time
begin_time = time.time()

#############
#check Satpy#
#############

#check if satpy has all the dependencies installed
#from satpy.utils import check_satpy
#check_satpy()

#check the readers name available in satpy
#print(satpy.available_readers())
#seviri_l1b_native

from readers.files_dirs import extract_yymmdd, path_to_file, path_dir_tree,  cth_fnames, path_ncdf
from figures.domain_info import domain_expats
from readers.msg_ncdf import read_dates


open_data = True
parallax_correction = False
domain = domain_expats
yy = '2023'
mm = '06'


def main():
        
    ###########
    #Open Data#
    ###########
    if open_data:
        
        # read file list of data to read 
        
        nat_fnames = sorted(glob(path_to_file+'/'+yy+'/'+mm+'/*NA.subset.nat'))
        
        print(len(nat_fnames))
        
        # remove from nat filelist the files in ncdf that are already processed
        nat_fnames_new = remove_processed_files(nat_fnames, path_dir_tree)
        
        print(len(nat_fnames_new))
        
        #Read nat files of msg data at different temporal steps
        for t,f in enumerate(nat_fnames_new):
                
            # reading file name
            file = f.split('/')[-1]
            #cth_file = cth_fnames[t].split('/')[-1]
            #print(file)

            #get start and end time from filename format yyyymmddhhmmss
            end_scan_time = file.split('-')[5].split('.')[0]
            time_str = datetime.datetime.strptime(end_scan_time, "%Y%m%d%H%M%S")
            print(time_str)
            
            #open msg file with Satpy
            scn = satpy.Scene(reader='seviri_l1b_native', filenames=[f]) #By default bad quality scan lines are masked and replaced with np.nan based on the quality flags provided by the data 
            
            # Check if the output directory exists
            if not os.path.exists(path_ncdf+'/'+yy+'/'+mm+'/'):
                # Create the directory if it doesn't exist
                os.makedirs(path_ncdf+'/'+yy+'/'+mm+'/')

            #get the lat/lon coords and store ncdf output file at first iteration
            if t == 0:
                lat_lon_ds = get_lats_lons(scn, domain, path_ncdf)
        
            #get the channel names
            channels = scn.available_dataset_names() 

            #esclude HRV channel
            channels = channels[1:]

            if parallax_correction:
                #create Scene for the parallax correction
                #scn = satpy.Scene({"seviri_l1b_native": [f], "cmsaf-claas2_l2_nc": [cth_fnames[t]]})
                scn = satpy.Scene({"seviri_l1b_native": [f], "nwcsaf-pps_nc": [cth_fnames[t]]})

            #TODO channels loop can be parallelized as the order is not important, use dask or multiporcessing 
            for i_ch, ch in enumerate(channels):
                
                # reading satellite channel data
                sat_da = read_channels(ch, scn, domain)
                
                # storing data in xarray dataset
                if i_ch == 0:
                    ds = xr.Dataset({str(ch):sat_da})
                else:
                    ds[str(ch)] = sat_da

                if parallax_correction:
                    ch = 'parallax_corrected_'+ch

            # Add a new dimension for the start time coordinate
            ds = ds.expand_dims('end_time', axis=0)
            ds['end_time'] = [time_str]
            

            # Set the directory path to save files
            #proj_file_path = path_to_file+'ncdf/'
            #if parallax_correction:
            #    proj_file_path = path_to_file+'HRSEVIRI_20210712_20210715_Parallax_Corrected/'

            ds.to_netcdf(path_ncdf+'/'+yy+'/'+mm+'/'+f.split('/')[-1].split('.')[0]+'.nc')
            print('product saved\n')
            
            #print(ds)

    # End time
    end_time = time.time()

    # Calculate elapsed time
    elapsed_time = end_time - begin_time
    # Path to the text file where you want to save the elapsed time
    output_file_path = path_to_file+'elapsed_time_satpy.txt'

    # Write elapsed time to the file
    with open(output_file_path, 'w') as file:
        print(f"Elapsed time: {elapsed_time} seconds", file=file)
    




def read_dates_nat(nat_fnames):
    """
    function to extract dates from filenames

    Args:
        filelist_ncdf (list of strings): list containing all filenames
    """    
    # number of characters before the date
    len_path = len(path_to_file)
    start = len('MSG3-SEVI-MSG15-0100-NA-')
    string_len = len('20230711')
    dates_all = [file[len_path+start:len_path+start+string_len] for file in nat_fnames]
    dates = np.asarray(dates_all)
    
    return np.unique(dates)
    
    
def remove_processed_files(nat_fnames, path_dir_tree):
    """
    removes filenames already processed by the nat filelist

    Args:
        nat_fnames (list): list of nat filenames
        path_dir_tree (string): string for output path of ncdf files 
        
    Dependencies:
    read_dates_nat 
    
    """
    
    # read dates from nat filelist
    dates = read_dates_nat(nat_fnames)

    # find dates to drop and if file exists, drop filename from list
    for ind_date, date in enumerate(dates):
        
        # reading year, month and day for building folder path
        yy,mm,dd = extract_yymmdd(date)
        
        # drop filename from nat filelist if daily ncdf file is created
        if os.path.exists( path_dir_tree+yy+'/'+mm+'/'+date+'_MSG_SEVIRI_EXPATS.nc'):
            # removing files with list comphrension
            for i, filename in enumerate(sorted(glob(path_to_file+'MSG3-SEVI-MSG15-0100-NA-'+date+"*"))):
                nat_fnames.remove(filename) 

    return nat_fnames


def get_lats_lons(scn, domain, path_out):
        """
        read satellite scene and extracts lats lons 

        Args:
            scn (satoy object): satellite scene object from satpy
            domain(list): domain coordinates 
            pah_out: output path where to save ncdf lat lon grid file
            
        returns:
        - saves lat lon grid ncdf file in path_out dir
        - returns lat_lon grid dataset
        """
        
        # reading domain information 
        minlon, maxlon, minlat, maxlat = domain

        #Load one channel
        scn.load(['IR_039'])       

        #Crop to area of interest
        crop_scn = scn.crop(ll_bbox=(minlon, minlat, maxlon, maxlat))

        #get coord in the cropped area
        area_crop = crop_scn['IR_039'].attrs['area'] #area in m
        sat_lon_crop, sat_lat_crop = area_crop.get_lonlats() #lat/lon grid (77,104)

        #get coords with parallax correction
        #sc = satpy.Scene({"seviri_l1b_hrit": files_l1b, "nwcsaf-geo": files_l2})
        #sc.load(["parallax_corrected_VIS006"])
        #get coord parallax corrected
        #area_plax_corr = sc['VIS006'].attrs['area'] #area in m
        #sat_lon_plax, sat_lat_plax = area_plax_corr.get_lonlats() #lat/lon grid (77,104)

        # create DataArrays with the coordinates using cloud mask grid
        lon_da = xr.DataArray(sat_lon_crop, dims=("y", "x"), name="lon")
        lat_da = xr.DataArray(sat_lat_crop, dims=("y", "x"), name="lat")

        # combine DataArrays into xarray object
        ds = xr.Dataset({"lon": lon_da, "lat": lat_da})
        if ~os.path.isfile(path_out+'lat_lon_grid.nc'):
            ds.to_netcdf(path_out+'lat_lon_grid.nc')
        
        return ds
    
def read_channels(ch, scn, domain):
    """
    function to read msg channels in xarray dataset

    Args:
        channels (list): list of channel names
    """
    # reading domain information 
    minlon, maxlon, minlat, maxlat = domain
    
    #Load channel
    scn.load([ch])       

    #Crop to area of interest
    crop_scn = scn.crop(ll_bbox=(minlon, minlat, maxlon, maxlat))

    #get data in the cropped area
    sat_data_crop = crop_scn[ch].values #R/Tb
    #print('sat data',sat_data_crop)
    
    #add channel values to the Dataset
    sat_da = xr.DataArray(sat_data_crop, dims=("y", "x"), name=str(ch))
    
    return(sat_da) 



if __name__ == "__main__":
    main()
    