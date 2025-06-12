import os
import io
import boto3
import logging
import pandas as pd
import xarray as xr
from cropping_functions import crops_nc_fixed, filter_by_domain, apply_cma_mask
from credentials_buckets import S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL

from config import *  # bring in X_PIXEL, Y_PIXEL, CLOUD_PRM, etc.

def read_crop_schedule(csv_path):
    df = pd.read_csv(csv_path)
    df['timestamp_list'] = df['timestamp_list'].apply(lambda x: x.split(','))
    return df

def create_filename(meta):
    ts_label = f"{'_'.join(meta['timestamps'])}"
    return f"{meta['sample_id']}_label{meta['label']}_dist{meta['distance']}_ul{meta['ul_lat']:.2f}_{meta['ul_lon']:.2f}_ts{ts_label}.nc"

def read_file_from_s3(s3, bucket, key):
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        return io.BytesIO(obj['Body'].read())
    except Exception as e:
        logging.error(f"Error reading {key} from S3: {e}")
        return None

def get_dataset_from_timestamps(s3, timestamp_list):
    datasets = []
    for ts in timestamp_list:
        year, month, day, hour = ts[:4], ts[5:7], ts[8:10], ts[11:13]
        file_path = f"/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN/{year}/{month}/merged_MSG_CMSAF_{year}-{month}-{day}.nc"
        obj = read_file_from_s3(s3, S3_BUCKET_NAME, file_path)
        if obj:
            ds = xr.open_dataset(obj)
            if set(CLOUD_PRM).issubset(ds.data_vars):
                ds_vars = ds[CLOUD_PRM]
                if APPLY_CMA and 'cma' in ds:
                    ds_vars = apply_cma_mask(ds, ds_vars, VALUE_MAX[0])
                try:
                    ds_filtered = ds_vars.sel(time=ts)
                    datasets.append(ds_filtered)
                except KeyError:
                    logging.warning(f"Timestamp {ts} not found in file.")
    if datasets:
        return xr.concat(datasets, dim="time")
    return None

def crop_fixed_from_csv(ds_crop, ul_lat, ul_lon, meta, outdir):
    filename = create_filename(meta)
    os.makedirs(outdir, exist_ok=True)
    save_path = os.path.join(outdir, filename)
    crops_nc_fixed(ds_crop, X_PIXEL, Y_PIXEL, [(ul_lat, ul_lon)], filename, outdir, file_format='nc')

def main(csv_path, outdir):
    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY
    )

    crop_df = read_crop_schedule(csv_path)

    for _, row in crop_df.iterrows():
        meta = {
            "ul_lat": row["ul_lat"],
            "ul_lon": row["ul_lon"],
            "label": row["label"],
            "distance": row["distance"],
            "sample_id": row["sample_id"],
            "timestamps": row["timestamp_list"]
        }

        ds_crop = get_dataset_from_timestamps(s3, meta["timestamps"])
        if ds_crop is None:
            logging.warning(f"Skipping {meta['sample_id']} due to missing data.")
            continue

        crop_fixed_from_csv(ds_crop, meta["ul_lat"], meta["ul_lon"], meta, outdir)

