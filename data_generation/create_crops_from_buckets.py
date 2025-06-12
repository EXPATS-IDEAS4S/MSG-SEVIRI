import os
import io
import boto3
import logging
from botocore.exceptions import ClientError
import xarray as xr
from scipy.ndimage import binary_closing
import numpy as np

from cropping_functions import crops_nc_random, crops_nc_fixed, filter_by_domain, filter_by_time
from credentials_buckets import S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL

def apply_cma_mask(ds_day, ds_day_var, value_max):
    """
    Applies binary closing to each time slice of the 'cma' field in ds_day,
    and updates 'ir_108' in ds_day_var accordingly at each timestamp.

    Parameters:
    - ds_day: xarray Dataset with dimensions (T, lat, lon) containing 'cma'.
    - ds_day_var: xarray Dataset with the same time dimension, containing 'ir_108'.
    - cloud_prm: list of strings indicating which cloud parameters are present.
    - value_max: value to assign where closed CMA mask is 0.

    Returns:
    - Updated ds_day_var with masked 'ir_108' for each time step.
    """
    
    structure = np.ones((3, 3), dtype=np.uint8)

    for t in ds_day['time']:
        cma_slice = ds_day['cma'].sel(time=t).values
        closed_cma = binary_closing(cma_slice, structure=structure)

        ir_108_slice = ds_day_var['IR_108'].sel(time=t)
        masked_ir_108 = ir_108_slice.where(closed_cma == 1, value_max)

        # Assign updated slice back to dataset
        ds_day_var['IR_108'].loc[dict(time=t)] = masked_ir_108

    return ds_day_var

def read_file(s3, file_name, bucket):
    """Upload a file to an S3 bucket
    :param s3: Initialized S3 client object
    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :return: object if file was uploaded, else False
    """
    try:
        #with open(file_name, "rb") as f:
        obj = s3.get_object(Bucket=bucket, Key=file_name)
        #print(obj)
        myObject = obj['Body'].read()
    except ClientError as e:
        logging.error(e)
        return None
    return myObject


# Initialize the S3 client
s3 = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_ACCESS_KEY
)

# List the objects in our bucket
response = s3.list_objects(Bucket=S3_BUCKET_NAME)
for item in response['Contents']:
    print(item['Key'])


#Directory with the data to uplad
years = [2013, 2014]
months = range(4,10)
days = range(1,32)
path_dir = f"/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN"
basename = "merged_MSG_CMSAF"

#Define crops setting

cropping_strategy = 'random' #random or fixed
n_samples = 1

# Define the cropping area for fixed crops (upper left corner latitude and longitude)
crop_ul_lon = 6.5
crop_ul_lat = 50.0

month_start = '04' #April
month_end = '09' #Septeber

hour_start = '00' #UTC (included)
hour_end = '24' #UTC (not included,

# Define your range limits
#TODO fix this in case more than one IR variable is included
value_min = 180.0  # Example minimum value
value_max = 320.0   # Example maximum value
 
x_pixel = 100 
y_pixel = 100 

domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper
domain_name = 'EXPATS'

cloud_prm = ['IR_108']#, 'WV_062', 'cma']#,'IR_039'] #'cot', WV_062, IR_039

apply_cma = True #if True, the cma variable will be included in the crops

file_extension = 'nc'  # File extension for the dataset files

#output_path =  f'/work/dcorradi/crops/{cloud_prm_str}_{years_str}_{x_pixel}x{y_pixel}_{domain_name}_{cropping_strategy}/'
outpath = f'/data1/crops/dcv2_ir108_100x100_test_tensor/{file_extension}/1'
os.makedirs(outpath, exist_ok=True)

for year in years:
    for month in months:
        month = f"{month:02d}"
        for day in days:
            file = f"{path_dir}/{year:04d}/{month}/{basename}_{year:04d}-{month}-{day:02d}.nc"
            print(file)
            #Read file from the bucket
            my_obj = read_file(s3, file, S3_BUCKET_NAME)
            if my_obj is not None:
                ds_day = xr.open_dataset(io.BytesIO(my_obj))
                #print(ds_day)
                
                #select only variable of interest
                ds_day_var = ds_day[cloud_prm]

                if apply_cma and 'cma' in ds_day and 'IR_108' in cloud_prm:
                    ds_day_var = apply_cma_mask(ds_day, ds_day_var, value_max)	

                #select only data within certain domain
                try:
                    ds_day_var = filter_by_domain(ds_day_var, domain)
                except ValueError as e:
                    print(f"Skipping file '{file}' due to error: {e}")
                    continue  # Skip this file and move to the next

                #extract timestamp
                timestamps = ds_day_var.time.values
                #print(timestamps)

                #loop through each daily file
                for timestamp in timestamps:
                    #extract hour
                    hour = str(timestamp).split('T')[1][0:2]
                    #print(hour)
                    #print(month)
                
                    #select the values for the current timestamp
                    try:
                        ds_time = filter_by_time(ds_day_var,timestamp)
                    except ValueError as e:
                        print(f"Skipping file '{file}-{timestamp}' due to error: {e}")
                        continue  # Skip this file and move to the next
                    #print(ds_time)
                    
                    # Check if the DataArray contains all NaN values
                    #is_all_nan_ds = xr.DataArray.isnull(ds_time).all()
                    #print(is_all_nan_ds)

                    # Check if all variables in the dataset are NaN
                    is_all_nan_ds = all([xr.DataArray.isnull(ds_time[var]).all() for var in ds_time.data_vars])
                    #print(is_all_nan_ds)

                    # Check if the dataset has values outside the defined range
                    is_outside_range = any([((ds_time[var] < value_min) | (ds_time[var] > value_max)).any() for var in ds_time.data_vars])
                    #print(is_outside_range)
                
                    #if there are no Nan, the months is between April and September 
                    if not is_all_nan_ds and not is_outside_range and month >= month_start and month <= month_end and hour >= hour_start and hour < hour_end:          

                        # saving cropped images
                        #filename_to_save = file.split('/')[-1].split('.')[0]+'_'+str(timestamp).split('T')[1][0:5]+'_'+domain_name
                        filename_to_save = str(timestamp).split('.')[0]
                        #print(filename_to_save)
                        
                        if cropping_strategy == 'random':
                            crops_nc_random(ds_time, x_pixel, y_pixel, n_samples, filename_to_save, outpath, file_extension)
                        elif cropping_strategy == 'fixed':
                            #print('fixed')
                            crops_nc_fixed(ds_time, x_pixel, y_pixel, [(crop_ul_lat,crop_ul_lon)], filename_to_save, outpath, file_extension)         
                        else:
                            raise ValueError(f"Invalid cropping strategy: '{cropping_strategy}'")
         

#nohup 3122484