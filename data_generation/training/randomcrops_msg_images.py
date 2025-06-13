"""
This script processes cropped satellite data to generate multiple random imgaes crops, applies cloud masking.

The script performs the following tasks:
1. Loads satellite data from NetCDF files, specifically focusing on a specified cloud parameter (e.g., 'IR_108').
2. Optionally applies a cloud mask to filter out non-cloudy areas, setting those pixels to a predefined field value.
3. Converts the cropped data to TIFF images, using specified colormaps and normalization bounds.

### Key Parameters:
- `cloud_prm`: The cloud parameter of interest (e.g., 'IR_108') that is used for processing.
- `crops_path`: Directory path containing the NetCDF files with the satellite image data.
- `cma_path`: Directory path containing the NetCDF files with cloud mask data.
- `apply_cma`: Boolean flag indicating whether to apply cloud masking.
- `out_dir`: Directory where cropped images and data will be saved.
- `x_pixel`, `y_pixel`: Dimensions of the random crops in pixels.
- `image_format`: The format of the output images (e.g., 'tif').
- `norm_types`: List of normalization methods to be applied (e.g., '10th-90th').
- `vmin`, `vmax`: Normalization bounds based on the selected statistics.
- `crop_file_list`: List of NetCDF files containing the satellite data to be processed.
- `cma_file_list`: List of NetCDF files containing the cloud mask data.

### Functions Used:
- `convert_crops_to_images(msg_ds, x_pixel, y_pixel, filename, image_format, out_dir, cmap, vmin, vmax, norm_type)`: Converts cropped data into image format.

### Usage:
1. Adjust the input parameters (e.g., `cloud_prm`, `crops_path`, `apply_cma`, `norm_types`) to fit the specific dataset and processing requirements.
2. Ensure that the directory structure and file paths for input data are correctly specified.

Author: Daniele Corradini
Affiliation: University of Cologne, Germany
Contact: dcorrad1@uni-koeln.de
"""
import xarray as xr
import os
from glob import glob
import time
import pandas as pd

from cropping_functions import convert_crops_to_images


start_time = time.time()

image_format = 'tif'

cloud_prm = 'IR_108' #'cot', WV_062, IR_039

cmap='Greys' #'Spectral_r' #Gray

colormode = 'greyscale'

x_pixel = 128
y_pixel = 128

crops_path = '/work/dcorradi/crops/case_studies/Marche_Flood_22/nc/'

cma_path = '/work/dcorradi/crops/case_studies/Marche_Flood_22/nc_clouds/'

apply_cma = True

out_dir = f'/work/dcorradi/crops/case_studies/Marche_Flood_22/'

crop_file_list = sorted(glob(crops_path+'*.nc'))
print('total msg crops are - '+ str(len(crop_file_list)))

cma_file_list = sorted(glob(cma_path+'*.nc'))
print('total cma crops are - '+ str(len(cma_file_list)))

if apply_cma and len(crop_file_list)!=len(cma_file_list):
    print('crops and cma do not match!')
    exit()

# Open the csv file with hte crops statistics
#crop_stat = os.path.join(out_dir, f'{cloud_prm}_statistics.csv')

if apply_cma:
    #crop_stat = os.path.join(out_dir, f'{cloud_prm}_statistics_CMA.csv')
    out_dir = out_dir+'CMA/'
    


#df = pd.read_csv(crop_stat)

# Define the name of the normalization depending on the lower and upper bounds
norm_types =  ['200K-300K'] #['Min-Max', '1th-99th', '5th-95th','10th-90th','25th-75th']

for norm_type in norm_types:
    print(norm_type)
    #get the right scaling
    vmin = 200 #df.loc[df['Statistic'] == norm_type.split('-')[0], 'Value'].values[0]
    vmax = 300 #df.loc[df['Statistic'] == norm_type.split('-')[1], 'Value'].values[0]

    #loop over the nc files containing the channel
    for msg_crop, cma_crop in zip(crop_file_list, cma_file_list): 
        #extract filename from path
        filename = msg_crop.split('/')[-1].split('.')[0] 
        print(filename)    

        #open the nc crop with xarray and select the desired variable
        msg_ds = xr.open_dataset(msg_crop)  
        msg_ds = msg_ds[cloud_prm]
        #print(ds) 

        #apply cloud mask
        if apply_cma:
            cma_ds = xr.open_dataset(cma_crop)
            cloud_mask = cma_ds['cma']

            msg_ds = msg_ds.where(cloud_mask == 1, vmax)
            

        convert_crops_to_images(msg_ds, x_pixel, y_pixel, filename, image_format, out_dir, cmap, vmin, vmax, norm_type, colormode, apply_cma)

print('crops conversion to images is done!')
            
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")            

