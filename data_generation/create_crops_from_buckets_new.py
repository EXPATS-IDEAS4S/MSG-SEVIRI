import os
import io
import logging
import xarray as xr
from datetime import datetime

from cropping_functions import crops_nc_random, crops_nc_fixed, filter_by_domain, filter_by_time, apply_cma_mask
from credentials_buckets import S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL
from config import *

import boto3
from botocore.exceptions import ClientError


def setup_logger():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def init_s3():
    return boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY
    )


def read_file(s3, file_path, bucket):
    try:
        obj = s3.get_object(Bucket=bucket, Key=file_path)
        return obj['Body'].read()
    except ClientError as e:
        logging.warning(f"Failed to read file {file_path}: {e}")
        return None


def is_valid_time(timestamp, month, day, hour):
    return (
        MONTH_START <= month <= MONTH_END and
        HOUR_START <= hour < HOUR_END and
        DAY_START <= day <= DAY_END 

    )


def process_timestamp(ds_time, file_name, timestamp, outpath):
    hour = str(timestamp).split('T')[1][0:2]

    is_all_nan_ds = all([xr.DataArray.isnull(ds_time[var]).all() for var in ds_time.data_vars])
    is_outside_range = any(
        [((ds_time[var] < vmin) | (ds_time[var] > vmax)).any()
         for var, vmin, vmax in zip(ds_time.data_vars, VALUE_MIN, VALUE_MAX)]
    )

    if is_all_nan_ds or is_outside_range:
        return

    if not is_valid_time(timestamp, file_name.split('-')[1], hour):
        return

    filename_to_save = f"{os.path.basename(file_name).split('.')[0]}_{hour}:{timestamp.minute:02d}_{DOMAIN_NAME}"

    if CROPPING_STRATEGY == 'random':
        crops_nc_random(ds_time, X_PIXEL, Y_PIXEL, N_SAMPLES, filename_to_save, outpath)
    elif CROPPING_STRATEGY == 'fixed':
        crops_nc_fixed(ds_time, X_PIXEL, Y_PIXEL, [(CROP_UL_LAT, CROP_UL_LON)], filename_to_save, outpath, 'npy')
    else:
        raise ValueError(f"Invalid cropping strategy: {CROPPING_STRATEGY}")


def main():
    setup_logger()
    s3 = init_s3()

    cloud_prm_str = "_".join(CLOUD_PRM)
    years_str = "-".join(map(str, YEARS))
    outpath = os.path.join(OUTPUT_BASE, f"crops_{cloud_prm_str}_{X_PIXEL}x{Y_PIXEL}_{years_str}_{N_SAMPLES}-{CROPPING_STRATEGY}/nc")
    os.makedirs(outpath, exist_ok=True)

    for year in YEARS:
        for month in MONTHS:
            for day in DAYS:
                file_path = f"{PATH_DIR}/{year:04d}/{month:02d}/{BASENAME}_{year:04d}-{month:02d}-{day:02d}.nc"
                logging.info(f"Processing file: {file_path}")
                file_obj = read_file(s3, file_path, S3_BUCKET_NAME)

                if file_obj is None:
                    continue

                ds_day = xr.open_dataset(io.BytesIO(file_obj))
                ds_day_var = ds_day[CLOUD_PRM]

                if APPLY_CMA and 'cma' in ds_day and 'IR_108' in CLOUD_PRM:
                    ds_day_var = apply_cma_mask(ds_day, ds_day_var, VALUE_MAX[0])

                try:
                    ds_day_var = filter_by_domain(ds_day_var, DOMAIN)
                except ValueError as e:
                    logging.warning(f"Skipping file due to domain error: {e}")
                    continue

                for timestamp in ds_day_var.time.values:
                    try:
                        ds_time = filter_by_time(ds_day_var, timestamp)
                        process_timestamp(ds_time, file_path, timestamp, outpath)
                    except Exception as e:
                        logging.warning(f"Skipping timestamp {timestamp} due to: {e}")


if __name__ == "__main__":
    main()
