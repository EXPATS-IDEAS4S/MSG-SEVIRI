"""
This script processes satellite image data to generate multiple random crops, saving them in NetCDF and TIFF formats.

The script performs the following tasks:
1. Reads and merges NetCDF files containing satellite data organized in monthly folders.
2. Filters the dataset by a specified geographical domain and time range.
3. Generates random crops from the dataset, ensuring they are free of NaN values.
4. Saves the cropped data in NetCDF format to retain original values and coordinates.
5. Saves the cropped images in TIFF format for visual inspection.

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
- `create_fig(image, pixel_size)`: Creates and returns a matplotlib figure with the given pixel size from an image.
- `multi_crops_param(file_path, image_path, filename)`: Generates random crops with various cloud parameters and saves them.
- `multi_crops_simple(ds_image, x_pixel, y_pixel, n_sample, filename, out_path)`: Generates multiple random crops from the input dataset and saves them.
- `filter_by_domain(ds, domain)`: Filters the input dataset based on a specified geographical domain.
- `filter_by_time(ds, time)`: Filters the input dataset based on a specified time.

Usage:
- Adjust the parameters as needed to fit the desired input data and output requirements.
- Ensure the input data is properly organized in the specified directory structure.

Author: Daniele Corradini
Affiliation: University of Cologne, Germany
Contact: dcorrad1@uni-koeln.de
"""
import numpy as np
import matplotlib.pyplot as plt
import datetime 
import xarray as xr
import os
import glob
from random import randrange
from PIL import Image
from datetime import datetime
import time

start_time = time.time()

#running nohup 127418

year = '2013'

msg_path = f'/data/sat/msg/netcdf/parallax/{year}/' #now it contains data only from Apr to Jul (like the COT from DC)
 
#merge all msg file in nc format (they are organized in months folders)
msg_org_files = glob.glob(os.path.join(msg_path,"*/*.nc")) 

print('total files are - '+ str(len(msg_org_files)))

month_start = '04' #April
month_end = '09' #Septeber

hour_start = '00' #UTC (included)
hour_end = '24' #UTC (not included, so if 18 it stop at 17.45, 24 will stop at 23.45 )
 
#pixels for the random crops
#org_pixel = 128 #DC crops with pixel resolution 2x1 km --> aound 0.02°x0.01°?
#TODO Crop size needs to be recalculated since I have 0.04°x0.04° resolution
#or I shold resample the data first
x_pixel = 128 #528
y_pixel = 128 #288

file_format = '.tif'
file_format1 = '.npy'
cloud_prm = 'IR_108' #'cot', WV_062, IR_039



#filter EXPATS domain to keep only Germany 
#domain = lonmin, lonmax, latmin, latmax = 6, 16, 48, 52 #DC domain from the paper
domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper
domain_name = 'EXPATS'

output_path =  f'/data/sat/msg/ml_train_crops/{cloud_prm}_{year}_{x_pixel}x{y_pixel}_{domain_name}/'

n_samples = 4

cmap='Spectral_r'


def create_fig(image, pixel_size, cmap, vmin=None, vmax=None):
    """
    Creates and returns a matplotlib figure with the given pixel size from an image.

    This function generates a matplotlib figure using the specified image and pixel size. 
    The figure is created with `dpi=1` to ensure the pixel size directly corresponds 
    to the figure size.

    :param image: The image to be plotted, compatible with matplotlib's imshow function.
    :param pixel_size: A tuple representing the pixel size (width, height) to be used as the figure size.
    :param vmin: The minimum data value that corresponds to the colormap's lower limit.
    :param vmax: The maximum data value that corresponds to the colormap's upper limit.
    :return: The created matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=pixel_size, dpi=1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.axis(False)
    plt.close(fig)
    return fig
    
    
def multi_crops_param(file_path, image_path, filename):
    img = Image.open(image_path)  
    x, y = img.size

    matrix = 128
    sample = 5
    sample_list = []
    
    x_pixel = 301
    y_pixel = 201

    new_x_pixel = 828    
    new_y_pixel = 488
    
    _file_lat = xarray.open_dataset(lat_lon_file).lat
    _file_lon = xarray.open_dataset(lat_lon_file).lon

    for i in range(sample):

        x1 = randrange(0, x - matrix)
        y1 = randrange(0, y - matrix)
        
        
        sds_profile = np.zeros((matrix, matrix))
        sds_profile.fill(np.nan)
        cot_profile = np.zeros((matrix, matrix))
        cot_profile.fill(np.nan)
        trs_profile = np.zeros((matrix, matrix))
        trs_profile.fill(np.nan)
        cth_profile = np.zeros((matrix, matrix))
        cth_profile.fill(np.nan)
        cph_profile = np.zeros((matrix, matrix))
        cph_profile.fill(np.nan)
        lat_profile = np.zeros((matrix, matrix))
        lat_profile.fill(np.nan)
        lon_profile = np.zeros((matrix, matrix))
        lon_profile.fill(np.nan)
        ctp_profile = np.zeros((matrix, matrix))
        ctp_profile.fill(np.nan)
        cldmask_profile = np.zeros((matrix, matrix))
        cldmask_profile.fill(np.nan)
        ctt_profile = np.zeros((matrix, matrix))
        ctt_profile.fill(np.nan)
        
        global_details = xarray.open_dataset(file_path).cot[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]  #entire domain?  
        cot_profile = global_details[y1:y1+ matrix,x1:x1 + matrix] #random crop?
        
        #if np.isnan(cot_profile).any() == False:
            
        sample_list.append(img.crop((x1, y1, x1 + matrix, y1 + matrix)))


        global_details = xarray.open_dataset(file_path).sds[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        sds_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]


        global_details = xarray.open_dataset(file_path).trs[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        trs_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]


        global_details = xarray.open_dataset(file_path).cth[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        cth_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]


        global_details = xarray.open_dataset(file_path).cph[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        cph_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]


        global_details = _file_lat[y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        lat_profile = _file_lat[y1:y1+ matrix,x1:x1 + matrix]


        global_details = _file_lon[y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        lon_profile = _file_lon[y1:y1+ matrix,x1:x1 + matrix]


        global_details = xarray.open_dataset(file_path).ctp[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        ctp_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]


        global_details = xarray.open_dataset(file_path).cldmask[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        cldmask_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]


        global_details = xarray.open_dataset(file_path).ctt[0,y_pixel:new_y_pixel,x_pixel:new_x_pixel]    
        ctt_profile = global_details[y1:y1+ matrix,x1:x1 + matrix]

        #It cropped all the variables in the small crop domain for each physical quantities, including lat/lon
        #then same them in a xarray dataset

        crop_data = xarray.Dataset(
            data_vars={

            "sds": (('lat','lon'), sds_profile, {'long_name': 'surface downwelling solar radiation', 'units':'W m-2', "standard_name": "sds"}),
            "cot": (('lat','lon'), cot_profile, {'long_name': 'atmosphere_optical_thickness_due_to_cloud', 'units':'', "standard_name": "cot"}),
            "trs": (('lat','lon'), trs_profile, {'long_name': 'TOA reflected solar radiation', 'units':'W m-2', "standard_name": "trs"}),
            "cth": (('lat','lon'), cth_profile, {'long_name': 'Cloud Top Altitude above geoid', 'units':'m', "standard_name": "cth"}),
            "cph": (('lat','lon'), cph_profile, {'long_name': 'thermodynamic_phase_of_cloud_water_particles_at_cloud_top status_flag', 'units':'1', "standard_name": "cph"}),
            "ctp": (('lat','lon'), ctp_profile, {'long_name': 'air_pressure_at_cloud_top', 'units':'hPa', "standard_name": "ctp"}),
            "cmask": (('lat','lon'), cldmask_profile, {'long_name': 'cloud_area_fraction status_flag', 'units':'1', "standard_name": "cmask"}),
            "ctt": (('lat','lon'), ctt_profile, {'long_name': 'air_pressure_at_cloud_top', 'units':'hPa', "standard_name": "ctt"}),
            },
            coords={
            "lat_crop": (('lat','lon'), lat_profile ,{"axis": "pressure_level","standard_name": "latitude","units": "degrees_north", "long_name":'pixel latitude'}), 
            "lon_crop": (('lat','lon'), lon_profile, {"axis": "pressure_level","standard_name": "longitude","units": "degrees_east", "long_name":'pixel longitude'}),
            },
            attrs={'CREATED_BY'     : 'Dwaipayan Chatterjee',
                    'CREATED_ON'       : str(datetime.now()),
                    'FILL_VALUE'       : 'NaN',
                    'IMAGE_NAME'       : filename, 
                    'PI_NAME'          : 'Dwaipayan Chatterjee',
                    'PI_AFFILIATION'   : 'University of Cologne (UNI), Germany',
                    'PI_ADDRESS'       : 'Institute for geophysics and meteorology, Pohligstrasse 3, 50969 Koeln',
                    'PI_MAIL'          : 'dchatter@meteo.uni-koeln.de',
                    'DATA_DESCRIPTION' : 'Macro-physics cloud parameters from Hartwig Deneke for random crops ',
                    'DATA_DISCIPLINE'  : 'Atmospheric Physics - Remote Sensing Radar Profiler',
                    'DATA_GROUP'       : 'MSG - MTG',
                    'DATA_LOCATION'    : 'Central European Domain',
                    'DATA_SOURCE'      : 'Hartwig_Leipzig_Tropos',
                    'DATA_PROCESSING'  : 'https://github.com/DC95/',
                    'COMMENT'          : '' }
        )

        crop_data = crop_data.assign_attrs({
            "Conventions": "CF-1.8",
            "title": crop_data.attrs["DATA_DESCRIPTION"],
            "institution": crop_data.attrs["PI_AFFILIATION"],
            "history": "".join([
                "source: " + crop_data.attrs["DATA_SOURCE"] + "\n",
                "processing: " + crop_data.attrs["DATA_PROCESSING"] + "\n",
                " adapted to enhance CF compatibility\n",
            ]),  # the idea of this attribute is that each applied transformation is appended to create something like a log
            "featureType": "trajectoryProfile",
        })
        #save 5 different crops
        crop_data.to_netcdf(cropped_image_additional+filename+"_germany_" +str(i)+'.nc')
        #print('filesave')

    
    for i in range(len(sample_list)):
        
        fig = create_fig(sample_list[i],[org_pixel,org_pixel],cropped_image_path+ '_germany'+file_format)
        fig.savefig(cropped_image_path + filename+ "_germany_" +str(i)+ file_format, dpi=1)


def multi_crops_simple(ds_image, x_pixel, y_pixel, n_sample, filename, out_path, cmap, vmin, vmax):
    """
    Generates multiple random crops from the input dataset, saves them in NetCDF and TIFF formats.

    This function takes an input dataset, generates random crops of specified size, and saves
    the crops as NetCDF files to preserve the original values and coordinates. Additionally,
    it saves the cropped images as TIFF files.

    :param ds_image: xarray.Dataset or xarray.DataArray
        The input dataset containing the image data along with latitude and longitude coordinates.
    :param x_pixel: int
        The width of the crop in pixels.
    :param y_pixel: int
        The height of the crop in pixels.
    :param n_sample: int
        The number of random crops to generate.
    :param filename: str
        The base filename for saving the cropped images.
    :param out_path: str
        The output directory where the cropped images will be saved.
    
    :return: None
    """

    #get array size from dataset ds_image 
    x = len(ds_image.lon.values)
    y = len(ds_image.lat.values)
    #print(x,y)
       
    for i in range(n_sample):

        x1 = randrange(0, x - x_pixel)
        y1 = randrange(0, y - y_pixel)
        #print(x1,y1)

        #find lat lon boundaries of the random crop
        latmin = ds_image.lat.values[y1]
        latmax = ds_image.lat.values[y1+y_pixel-1]
        lonmin = ds_image.lon.values[x1]
        lonmax = ds_image.lon.values[x1+x_pixel-1]
        #print([lonmin, lonmax, latmin, latmax])

        #crop the dataset besed on the random x and y (the upper left point of the crop)
        ds_crop = filter_by_domain(ds_image,[lonmin, lonmax, latmin, latmax])
        #print(ds_crop)

        #check if the crop contains any Nan
        isnan_ds = xr.DataArray.isnull(xr.DataArray.sum(ds_crop,skipna=False))

        if isnan_ds==False:
            #save the crops in nc format to keep actual values and lat/lon coordinates
            ds_crop.to_netcdf(out_path+'nc/'+filename+"_"+str(i)+'.nc')
            
            #save the RGB images
            fig = create_fig(ds_crop.values.squeeze(),[x_pixel,y_pixel], cmap, vmin, vmax)
            fig.savefig(out_path+'tif/'+filename+"_"+str(i)+'.tif', dpi=1)

            print(out_path+'tif/'+filename+"_"+str(i), 'saved')


def filter_by_domain(ds, domain):
    """
    Filters the input dataset based on a specified geographical domain.

    This function applies a mask to the input dataset to include only the data
    points within the specified latitude and longitude boundaries. The masked 
    dataset is then returned.

    :param ds: xarray.Dataset or xarray.DataArray
        The input dataset containing the data to be filtered.
    :param domain: list or tuple of float
        A list or tuple specifying the domain boundaries in the format 
        [lonmin, lonmax, latmin, latmax], where:
        - lonmin: Minimum longitude
        - lonmax: Maximum longitude
        - latmin: Minimum latitude
        - latmax: Maximum latitude
    
    :return: xarray.Dataset or xarray.DataArray
        The dataset filtered by the specified geographical domain.
    """
    lonmin, lonmax, latmin, latmax = domain
    #Find the mask
    mask = (ds['lat'] >= latmin) & (ds['lat'] <= latmax) & (ds['lon'] >= lonmin) & (ds['lon'] <= lonmax)
    
    # Apply the mask to the dataset
    ds_masked = ds.where(mask, drop=True)

    return ds_masked

def filter_by_time(ds, time):
    """
    Filters the input dataset based on a specified time.

    This function applies a mask to the input dataset to include only the data
    points that match the specified time. The masked dataset is then returned.

    :param ds: xarray.Dataset or xarray.DataArray
        The input dataset containing the data to be filtered.
    :param time: datetime-like object
        The specific time for which the data should be filtered. This can be a 
        datetime object or any other type compatible with the dataset's time coordinate.
    
    :return: xarray.Dataset or xarray.DataArray
        The dataset filtered by the specified time.
    """
    #Find the mask
    mask = (ds['time'] == time)
    
    # Apply the mask to the dataset
    ds_masked = ds.where(mask, drop=True)

    return ds_masked


#TODO do it with quantiles to avoid outliers, but in a incremental way
def compute_global_min_max(file_paths, variable):
    """
    Compute the global minimum and maximum values across all NetCDF datasets.

    :param file_paths: List of paths to NetCDF files.
    :param variable: The variable to analyze.
    :return: (global_min, global_max) values.
    """
    global_min = float('inf')
    global_max = float('-inf')

    for path in file_paths:
        ds = xr.open_dataset(path)
        data = ds[variable].values
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
        
        # Update global min and max
        global_min = min(global_min, data_min)
        global_max = max(global_max, data_max)
        
        ds.close()

    return global_min, global_max
            

# Check if the directory exists
if not os.path.exists(output_path):
    # Create the directory if it doesn't exist
    os.makedirs(output_path) 

# Check if the directory exists
if not os.path.exists(output_path+'nc/'):
    # Create the directory if it doesn't exist
    os.makedirs(output_path+'nc/')

# Check if the directory exists
if not os.path.exists(output_path+'tif/'):
    # Create the directory if it doesn't exist
    os.makedirs(output_path+'tif/')

global_min_max_path = os.path.join(output_path, 'global_min_max.npy')

# Check if the min-max values are already saved
if os.path.exists(global_min_max_path):
    vmin, vmax = np.load(global_min_max_path)
    print(f'Loaded global min: {vmin} and global max: {vmax}')
else:
    # Compute max and min for normalizing the colormaps
    vmin, vmax = compute_global_min_max(msg_org_files, cloud_prm)
    print(f'Computed global min: {vmin} and global max: {vmax}')
    np.save(global_min_max_path, np.array([vmin, vmax]))

exit()

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
    #print(ds_day)

    #select only variable of interest
    ds_day = ds_day[cloud_prm]

    #select only data within certain domain
    ds_day = filter_by_domain(ds_day, domain)
    #print(ds_day)

    #extract timestamp
    timestamps = ds_day.time.values
    #print(timestamps)

    #loop through each daily file
    for timestamp in timestamps:
        #extract hour
        hour = str(timestamp).split('T')[1][0:2]
        #print(hour)

        #select the values for the current timestamp
        ds_time = filter_by_time(ds_day,timestamp)

        # Check if the DataArray contains all NaN values
        is_all_nan_ds = xr.DataArray.isnull(ds_time).all()

        #if there are no Nan, the months is between April and September and time is before 17 UTC
        if is_all_nan_ds == False and month >= month_start and month <= month_end and hour >= hour_start and hour < hour_end:
            #print(timestamp)            

            # saving cropped images
            filename_to_save = filename.split('-')[0]+'_'+str(timestamp).split('T')[1][0:5]+'_'+domain_name
            print(filename_to_save)
            multi_crops_simple(ds_time, x_pixel, y_pixel, n_samples, filename_to_save, output_path, cmap, vmin, vmax)

print('crops generation is done!')
            
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")            