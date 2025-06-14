"""
This script processes satellite image data to generate multiple random crops, saving them in NetCDF.

The script performs the following tasks:
1. Reads and merges NetCDF files containing satellite data organized in monthly folders.
2. Filters the dataset by a specified geographical domain and time range.
3. Generates random crops from the dataset, ensuring they are free of NaN values.
4. Saves the cropped data in NetCDF format, retaining also the coordinates.

Key parameters:
- `year`: Year of the data to process.
- `msg_path`: Path to the directory containing the NetCDF files.
- `output_path`: Directory where cropped images and data will be saved.
- `month_start`, `month_end`: Range of months to process.
- `hour_start`, `hour_end`: Range of hours (UTC) to process.
- `x_pixel`, `y_pixel`: Dimensions of the random crops in pixels.
- `n_samples`: Number of random crops to generate per dataset.
- `domain`: Geographical domain boundaries for filtering the data.
- `cloud_prm`: Cloud parameter of interest (e.g., 'IR_108').

The script uses the following functions:
- `crops_nc`: Creates the crops in xarray format and save it in netcdf 
- `filter_by_domain(ds, domain)`: Filters the input dataset based on a specified geographical domain.
- `filter_by_time(ds, time)`: Filters the input dataset based on a specified time.

Usage:
- Adjust the parameters as needed to fit the desired input data and output requirements.
- Ensure the input data is properly organized in the specified directory structure.

Author: Daniele Corradini
Affiliation: University of Cologne, Germany
Contact: dcorrad1@uni-koeln.de
"""

import xarray as xr
import os
import glob
import time

from cropping_functions import crops_nc_random, crops_nc_fixed, filter_by_domain, filter_by_time

start_time = time.time()

years = ['2013','2014','2015'] #1 year is 17568 samples

cropping_strategy = 'random' #random or fixed

month_start = '04' #April
month_end = '09' #Septeber

hour_start = '00' #UTC (included)
hour_end = '24' #UTC (not included, so if 18 it stop at 17.45, 24 will stop at 23.45 )

# Define your range limits
value_min = [180.0]  # Example minimum value
value_max = [350.0]   # Example maximum value
 
#pixels for the random crops
#org_pixel = 128 #DC crops with pixel resolution 2x1 km --> aound 0.02°x0.01°?
#TODO Crop size needs to be recalculated since I have 0.04°x0.04° resolution
#or I shold resample the data first
x_pixel = 200 #528
y_pixel = 200 #288

cloud_prm = ['IR_108']#,'WV_062','IR_039'] #'cot', WV_062, IR_039

#filter EXPATS domain to keep only Germany 
#domain = lonmin, lonmax, latmin, latmax = 6, 16, 48, 52 #DC domain from the paper
domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper
domain_name = 'EXPATS'

crop_ul_lon = 6.5
crop_ul_lat = 50.0

n_samples = 1

# Join the elements of the lists with '-'
cloud_prm_str = '-'.join(cloud_prm)
years_str = '-'.join(years)

#define output path
output_path =  f'/work/dcorradi/crops/{cloud_prm_str}_{years_str}_{x_pixel}x{y_pixel}_{domain_name}_{cropping_strategy}/'

# Check if the directory exists
if not os.path.exists(output_path+'nc/'):
    # Create the directory if it doesn't exist
    os.makedirs(output_path+'nc/')

#loop over the years
for year in years:

    msg_path = f'/data/sat/msg/netcdf/parallax/{year}/'

    #merge all msg file in nc format (they are organized in months folders)
    msg_org_files = glob.glob(os.path.join(msg_path,"*/*.nc")) #[:10] #for testing

    print('total files are - '+ str(len(msg_org_files)))
   
    #loop over the nc files containing the channel
    for file in msg_org_files: 
        #extract filename from path
        filename = file.split('/')[-1] 
        print(filename)

        #extract months from filename
        month = filename.split('-')[0][4:6]
        #print(month)

        #open daily dataset
        ds_day = xr.open_dataset(file)

        #select only variable of interest
        ds_day = ds_day[cloud_prm]         

        #select only data within certain domain
        try:
            ds_day = filter_by_domain(ds_day, domain)
        except ValueError as e:
            print(f"Skipping file '{filename}' due to error: {e}")
            continue  # Skip this file and move to the next

        #extract timestamp
        timestamps = ds_day.time.values
        #print(timestamps)

        #loop through each daily file
        for timestamp in timestamps:
            #extract hour
            hour = str(timestamp).split('T')[1][0:2]
            #print(hour)

            #select the values for the current timestamp
            try:
                ds_time = filter_by_time(ds_day,timestamp)
            except ValueError as e:
                print(f"Skipping file '{filename}-{timestamp}' due to error: {e}")
                continue  # Skip this file and move to the next

            # Check if the DataArray contains all NaN values
            #is_all_nan_ds = xr.DataArray.isnull(ds_time).all()
            #print(is_all_nan_ds)

            # Check if all variables in the dataset are NaN
            is_all_nan_ds = all([xr.DataArray.isnull(ds_time[var]).all() for var in ds_time.data_vars])
            #print(is_all_nan_ds)

            # Check if the dataset has values outside the defined range
            is_outside_range = any([((ds_time[var] < value_min) | (ds_time[var] > value_max)).any() for var in ds_time.data_vars])

            #if there are no Nan, the months is between April and September 
            if not is_all_nan_ds and not is_outside_range and month >= month_start and month <= month_end and hour >= hour_start and hour < hour_end:
                print(timestamp)            

                # saving cropped images
                filename_to_save = filename.split('-')[0]+'_'+str(timestamp).split('T')[1][0:5]+'_'+domain_name
                #print(filename_to_save)
                if cropping_strategy == 'random':
                    crops_nc_random(ds_time, x_pixel, y_pixel, n_samples, filename_to_save, output_path)
                elif cropping_strategy == 'fixed':
                    #print('fixed')
                    crops_nc_fixed(ds_time, x_pixel, y_pixel, [(crop_ul_lat,crop_ul_lon)], filename_to_save, output_path)          
                else:
                    raise ValueError(f"Invalid cropping strategy: '{cropping_strategy}'")


print('crops generation is done!')
            
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")  
        

