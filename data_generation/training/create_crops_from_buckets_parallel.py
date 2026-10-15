import os
import io
import boto3
import logging
from botocore.exceptions import ClientError
import xarray as xr
import numpy as np
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.append('/home/Daniele/codes/MSG-SEVIRI/data_generation/')

from cropping_functions import crops_nc_random, crops_nc_fixed, filter_by_domain, filter_by_time, apply_cma_mask
from credentials_buckets import S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL


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
value_min = [180.0, 200]  # Example minimum value
value_max = [320.0, 260]   # Example maximum value

# Set this to True if 6.2-10.8 difference shoul be used 
OT = True 
 
x_pixel = 100 
y_pixel = 100 

domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper
domain_name = 'EXPATS'

cloud_prm = ['IR_108', 'WV_062']#, 'cma']#,'IR_039'] #'cot', WV_062, IR_039

apply_cma = True #if True, the cma variable will be included in the crops

file_extension = 'nc'  # File extension for the dataset files

#output_path =  f'/work/dcorradi/crops/{cloud_prm_str}_{years_str}_{x_pixel}x{y_pixel}_{domain_name}_{cropping_strategy}/'
outpath = f'/data1/crops/dcv2_ir108_OT_100x100_35k_nc/{file_extension}/1'
os.makedirs(outpath, exist_ok=True)

def process_file(year, month, day):
    file = f"{path_dir}/{year:04d}/{month:02d}/{basename}_{year:04d}-{month:02d}-{day:02d}.nc"
    print(file)
    
    my_obj = read_file(s3, file, S3_BUCKET_NAME)
    if my_obj is None:
        return
    
    try:
        ds = xr.open_dataset(io.BytesIO(my_obj))
        ds = filter_by_domain(ds, domain)
        ds_var = ds[cloud_prm]
        ds_var = filter_by_domain(ds_var, domain)
    except Exception as e:
        print(f"Skipping {file} due to error: {e}")
        return
    
    if OT and 'WV_062' in ds_var and 'IR_108' in ds_var:
        ds_var['WV_062'] = ds_var['WV_062'] - ds_var['IR_108']
        ds_var = ds_var.rename({'WV_062': 'WV_062-IR_108'})
        value_max[1] = -60.0

    for timestamp in ds_var.time.values:
        hour = int(str(timestamp)[11:13])
        if not (month_start <= int(month) <= month_end and hour_start <= hour < hour_end):
            continue

        try:
            ds_t = filter_by_time(ds, timestamp)
            ds_t_var = filter_by_time(ds_var, timestamp)
        except:
            continue
        
        if apply_cma and 'cma' in ds_t and 'IR_108' in cloud_prm:
            ds_t_var = apply_cma_mask(ds_t, ds_t_var, value_max, only_108=False)
        
        is_all_nan = ds_t_var.to_array().isnull().all()
        is_out_of_bounds = ((ds_t_var < value_min) | (ds_t_var > value_max)).any()
        
        if not is_all_nan and not is_out_of_bounds:
            fname = str(timestamp).split('.')[0]
            if cropping_strategy == 'random':
                crops_nc_random(ds_t_var, x_pixel, y_pixel, n_samples, fname, outpath, file_extension)
            elif cropping_strategy == 'fixed':
                crops_nc_fixed(ds_t_var, x_pixel, y_pixel, [(crop_ul_lat, crop_ul_lon)], fname, outpath, file_extension)

# Run with parallelism
with ThreadPoolExecutor(max_workers=8) as executor:
    for year in years:
        for month in months:
            for day in days:
                executor.submit(process_file, year, month, day)