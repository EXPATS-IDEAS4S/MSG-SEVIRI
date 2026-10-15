import os
import io
import xarray as xr
import numpy as np
import boto3
from botocore.exceptions import ClientError
import sys
from datetime import datetime, timedelta
import pandas as pd


sys.path.append('/home/Daniele/codes/MSG-SEVIRI/data_generation/')
from cropping_functions import crops_nc_fixed, filter_by_domain, filter_by_time, apply_cma_mask
from credentials_buckets import S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL

# === CONFIG ===
INPUT_DIR = "/sat_data/crops/2006-2023_4-9_areathresh30_res15min_4frames_gap15min_cropsize128_min5pix"
OUTPUT_DIR = "/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nc"
os.makedirs(OUTPUT_DIR, exist_ok=True)

path_dir = f"/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN"
basename = "merged_MSG_CMSAF"

# Select channels
SELECT_CHANNELS = ["IR_108"]  # or None for all
APPLY_CLOUD_MASK = True
OT=False

max_domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper

# Resize crop size
NEW_SIZE = 75  # set < 128 for central crop, or > 128 for larger crops fetched from bucket
GRID_RES = 0.04

value_min = [180.0]  # Example minimum value
value_max = [320.0]

if OT:
    value_fields = [value_max[0]] 
else:
    value_fields = [value_max[0]]

# Adjust time dimension
NEW_FRAMES = 5  # set <4 → keep last N, set >4 → extend backwards using bucket
TIME_RES = "15T" #minus for backwords in time

# Label regrouping
LABEL_MAPPING = {
    "hail": ["4_super_hail", "3_large_hail", "2_hail_initiation_graupel"],
    "no_hail": ["0_no_hail", "1_hail_potential"]
}


# --- Helpers ---
def read_file_s3(s3, file_name, bucket):
    try:
        obj = s3.get_object(Bucket=bucket, Key=file_name)
        return obj["Body"].read()
    except ClientError as e:
        print(f"S3 error {file_name}: {e}")
        return None


def center_crop(da, new_size):
    """Crop the center of a square DataArray."""
    orig_size = da.sizes["lat"]
    start = (orig_size - new_size) // 2
    return da.isel(lat=slice(start, start + new_size), lon=slice(start, start + new_size))


# Init S3 client
s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_ACCESS_KEY,
)


# --- Main loop ---
for root, dirs, files in os.walk(INPUT_DIR):
    print(root, dirs,files)
    exit()
    for f in files:
        if not f.endswith(".nc"):
            continue

        in_path = os.path.join(root, f)
        print(f"Processing {in_path}")

        #extract hail probability class from path
        hail_prob_class = in_path.split('/')[-2]
        #print(hail_prob_class)

        try:
            ds_in = xr.open_dataset(in_path, engine='h5netcdf')
            #print(ds_in)

            # Extract lat/lon/time from hail crop
            lat = float(ds_in.attrs["hail_area_lat"])
            lon = float(ds_in.attrs["hail_area_lon"])
        
            # Parse end_time string "YYYYMMDD_HHMM" → datetime64
            end_time_str = ds_in.attrs["end_time"]
            end_time = datetime.strptime(end_time_str, "%Y%m%d_%H%M")
            end_time = np.datetime64(end_time)

            print(f" Center: ({lat:.3f}, {lon:.3f}), End time: {end_time_str}")

            date = end_time_str.split('_')[0]
            time = end_time_str.split('_')[1]

            year, month, day = date[:4], date[4:6], date[6:8]
            hour, minute = time[:2], time[2:4]
            print(f" Date: {year}-{month}-{day}, Time: {hour}:{minute}")

            file = f"{path_dir}/{year}/{month}/{basename}_{year}-{month}-{day}.nc"
            #print(file)

            obj = read_file_s3(s3, file, S3_BUCKET_NAME)
            if obj is None:
                print(f"Missing {file}, skipping")
                continue

            ds_day = xr.open_dataset(io.BytesIO(obj))
            #print(ds_day)

            # Channel selection
            ds_day_var = ds_day[SELECT_CHANNELS]

            #select only data within certain domain
            #make domain using the lat lon centers and the size
            #domain of this form: domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper
            

            domain = [
                lon - NEW_SIZE * GRID_RES / 2,
                lon + NEW_SIZE * GRID_RES / 2,
                lat - NEW_SIZE * GRID_RES / 2,
                lat + NEW_SIZE * GRID_RES / 2
            ]

            # Adjust domain to stay within max_domain
            domain_width = domain[1] - domain[0]
            domain_height = domain[3] - domain[2]

            # Shift in longitude if it goes out of bounds
            if domain[0] < max_domain[0]:
                domain[0] = max_domain[0]
                domain[1] = max_domain[0] + domain_width
            elif domain[1] > max_domain[1]:
                domain[1] = max_domain[1]
                domain[0] = max_domain[1] - domain_width

            # Shift in latitude if it goes out of bounds
            if domain[2] < max_domain[2]:
                domain[2] = max_domain[2]
                domain[3] = max_domain[2] + domain_height
            elif domain[3] > max_domain[3]:
                domain[3] = max_domain[3]
                domain[2] = max_domain[3] - domain_height

            print(f"Adjusted domain: {domain}")

            print(domain)
            #check if domain  goes beyond the max_domain
            if domain[0] < max_domain[0] or domain[1] > max_domain[1] or domain[2] < max_domain[2] or domain[3] > max_domain[3]:
                print(f"⚠ Domain {domain} goes beyond max_domain {max_domain}, skipping")
                #TODO fix this problem, to skip less samples
                continue

            try:
                ds_day_var = filter_by_domain(ds_day_var, domain)
                ds_day = filter_by_domain(ds_day, domain)
            except ValueError as e:
                print(f"Skipping file '{file}' due to error: {e}")
                continue  # Skip this file and move to the next

            

            lat_size = ds_day_var.sizes['lat']
            lon_size = ds_day_var.sizes['lon']

            # Check latitude
            if lat_size > NEW_SIZE:
                # Trim equally from both ends
                extra = lat_size - NEW_SIZE
                start = extra // 2
                end = start + NEW_SIZE
                ds_day_var = ds_day_var.isel(lat=slice(start, end))
                ds_day = ds_day.isel(lat=slice(start, end))
            elif lat_size < NEW_SIZE:
                print(f"Skipping file '{file}' due to latitude size < NEW_SIZE: {lat_size}")
                continue

            # Check longitude
            if lon_size > NEW_SIZE:
                extra = lon_size - NEW_SIZE
                start = extra // 2
                end = start + NEW_SIZE
                ds_day_var = ds_day_var.isel(lon=slice(start, end))
                ds_day = ds_day.isel(lon=slice(start, end))
            elif lon_size < NEW_SIZE:
                print(f"Skipping file '{file}' due to longitude size < NEW_SIZE: {lon_size}")
                continue

            # Now both dimensions are exactly NEW_SIZE
            print(f"Final size after trimming: {ds_day_var.sizes}")

            #check if the filte by domain worked properly by checking size of lat lon correspond to NEW_SIZE
            if ds_day_var.sizes['lat'] != NEW_SIZE or ds_day_var.sizes['lon'] != NEW_SIZE:
                print(f"Skipping file '{file}' due to size mismatch after domain filter: {ds_day_var.sizes}")
                #TODO fix this problem to skip less samples
                continue  # Skip this file and move to the next

            try:
            # --- Build the desired time range ---
                timestamps = pd.date_range(
                    end=end_time,                # include end_time
                    periods=NEW_FRAMES,          # how many frames
                    freq=TIME_RES                # e.g., '15T'
                )
                timestamps = timestamps.sort_values()
                #print("Requested time range:", timestamps)

                # --- If timestamps cross into previous day, load that file too ---
                end_date = pd.to_datetime(end_time).date()   # ensure it's a date
                if timestamps.min().date() < end_date:
                    prev_day = (pd.to_datetime(end_time) - timedelta(days=1)).strftime("%Y-%m-%d")
                    prev_year, prev_month, prev_daynum = prev_day.split("-")
                    prev_file = f"{path_dir}/{prev_year}/{prev_month}/{basename}_{prev_year}-{prev_month}-{prev_daynum}.nc"
                    print(f"⚠ Timestamps extend into previous day, need {prev_file}")

                    obj_prev = read_file_s3(s3, prev_file, S3_BUCKET_NAME)
                    if obj_prev is not None:
                        ds_prev = xr.open_dataset(io.BytesIO(obj_prev))
                        ds_prev_var = ds_prev[SELECT_CHANNELS]

                        # Apply domain filter to prev_day as well
                        ds_prev_var = filter_by_domain(ds_prev_var, domain)
                        ds_prev = filter_by_domain(ds_prev, domain)

                        # Merge with current day
                        ds_day_var = xr.concat([ds_prev_var, ds_day_var], dim="time")
                        ds_day     = xr.concat([ds_prev, ds_day], dim="time")
                    else:
                        print(f"⚠ Missing previous day file {prev_file}, will only use current day")

                # --- Now select the requested timestamps from the merged dataset ---
                ds_time_var = filter_by_time(ds_day_var, timestamps)
                ds_time     = filter_by_time(ds_day, timestamps)

                # --- Check completeness ---
                if ds_time.sizes["time"] != NEW_FRAMES:
                    print(f"⚠ Incomplete sequence: expected {NEW_FRAMES}, got {ds_time.sizes['time']}")
                    continue

            except ValueError as e:
                print(f"Skipping file '{file}-{end_time}' due to error: {e}")
                continue  # Skip this file and move to the next
                
            #print(ds_time_var)


            # Check if all variables in the dataset are NaN
            #TODO check this since I got many files with NaN at the end of the process
            is_all_nan_ds = all([xr.DataArray.isnull(ds_time_var[var]).all() for var in ds_time_var.data_vars])
            #print(is_all_nan_ds)

            # Check if the dataset has values outside the defined range
            is_outside_range = any([((ds_time_var[var] < value_min[i]) | (ds_time_var[var] > value_max[i])).any() for i,var in enumerate(ds_time_var.data_vars)])
            #print(is_outside_range)


            #if there are no Nan, the months is between April and September 
            if not is_all_nan_ds and not is_outside_range:
                print(f"Processing file: {file} for timestamp: {end_time}")
                # saving cropped images
                #filename_to_save = file.split('/')[-1].split('.')[0]+'_'+str(timestamp).split('T')[1][0:5]+'_'+domain_name
                #filename_to_save = str(timestamp).split('.')[0]
                #print(filename_to_save)

                if OT:
                    #print(f"Applying OT to {filename_to_save}")
                    #substitute channl WV_062 with the difference WV_062-IR_108
                    ds_time_var['WV_062'] = ds_time_var['WV_062'] - ds_time_var['IR_108']
                    #the rename the variable to WV_062-IR_108
                    ds_time_var = ds_time_var.rename({'WV_062': 'WV_062-IR_108'})
            
                if APPLY_CLOUD_MASK and 'cma' in ds_time and 'IR_108' in SELECT_CHANNELS:
                    #apply value filds depending if OT is True or False
                    ds_time_var = apply_cma_mask(ds_time, ds_time_var, value_fields, only_108=False)
                    #print(ds_time_var)
                    #print('cloud mask')

                
                # Save under regrouped label dir
                parent_label = os.path.basename(root)
                new_label = next((k for k, v in LABEL_MAPPING.items() if parent_label in v), parent_label)
                out_dir = os.path.join(OUTPUT_DIR, new_label)
                #print(out_dir)
                os.makedirs(out_dir, exist_ok=True)

                
                # Format end_time as "YYYYMMDD_HHMM"
                end_time_str = np.datetime_as_string(end_time, unit="m").replace("-", "").replace(":", "").replace("T", "_")

                # Build config part
                time_res_str = TIME_RES.replace("T", "min")  # "15T" -> "15min"
                config_part = f"res{time_res_str}_{NEW_FRAMES}frames_cropsize{NEW_SIZE}"

                # Build full filename
                fname = f"{end_time_str}_{config_part}_{hail_prob_class}.nc"
                #print(fname)

                out_path = os.path.join(out_dir, fname)
                encoding = {
                                var: {
                                    'zlib': True,
                                    'complevel': 9,
                                    'dtype': ds_time_var[var].dtype.name  # preserve original dtype (e.g., 'float32', 'int16')
                                } for var in ds_time_var.data_vars
                            }
                ds_time_var.to_netcdf(out_path, encoding=encoding, engine='h5netcdf')
                ds_time_var.close()
                print(f"Saved {out_path}")

        except Exception as e:
            print(f"Error processing file {file}: {e}")
            continue

#nohup 356528