"""
This script processes satellite image data to generate multiple random crops, saving them in NetCDF and TIFF formats.

The script performs the following tasks:
1. Reads and merges NetCDF files containing satellite data organized in monthly folders.
2. Filters the dataset by a specified geographical domain and time range.
3. Generates random crops from the dataset, ensuring they are free of NaN values.
1. Saves the cropped data in NetCDF format to retain original values and coordinates.
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
from glob import glob
from random import randrange
from PIL import Image
from datetime import datetime
import time
import pandas as pd

from cropping_functions import convert_crops_to_images


start_time = time.time()

image_format = 'tif'

cloud_prm = 'IR_108' #'cot', WV_062, IR_039

cmap='Greys' #'Spectral_r' #Gray

x_pixel, y_pixel = 128

crops_path = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc/'

out_dir = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/'

# Check if the directory exists
if not os.path.exists(out_dir):
    # Create the directory if it doesn't exist
    os.makedirs(out_dir) 


crop_file_list = sorted(glob(crops_path+'*.nc'))
print('total files are - '+ str(len(crop_file_list)))

# Open the csv file with hte crops statistics
crop_stat = os.path.join(out_dir, f'{cloud_prm}_statistics.csv')
df = pd.read_csv(crop_stat)

# Define the name of the normalization depending on the lower and upper bounds
norm_types = ['Min-Max', '1th-99th', '5th-95th']

for norm_type in norm_types:
    #get the right scaling
    vmin = df.loc[df['Statistic'] == norm_type.split('-')[0], 'Value'].values[0]
    vmax = df.loc[df['Statistic'] == norm_type.split('-')[1], 'Value'].values[0]

    #loop over the nc files containing the channel
    for file in crop_file_list: 
        #extract filename from path
        filename = file.split('/')[-1].split('.')[0] 
        print(filename)    

        #open the nc crop with xarray
        ds = xr.open_dataset(file)            

        convert_crops_to_images(ds, x_pixel, y_pixel, filename, image_format, out_dir, cmap, vmin, vmax, norm_type)

print('crops conversion to images is done!')
            
end_time = time.time()

elapsed_time = end_time - start_time
print(f"Total execution time: {elapsed_time:.2f} seconds")            