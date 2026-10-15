import os
import io
import boto3
import logging
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
import sys

sys.path.append('/home/Daniele/codes/MSG-SEVIRI/data_generation')
from cropping_functions import crops_nc_fixed, apply_cma_mask
from credentials_buckets import S3_BUCKET_NAME, S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL
from training.config import *

logging.basicConfig(level=logging.INFO)

def parse_filename(filename):
    parts = os.path.basename(filename).split('_')
    dt_str = parts[0]
    lat = float(parts[1])
    lon = float(parts[2])
    grid_size = float(parts[3])
    date_str, time_str = dt_str.split('-')
    return date_str, time_str, lat, lon, grid_size

def generate_timestamps(date_str, time_str, delta_minutes=15, steps=12):
    base = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    return [(base + timedelta(minutes=delta_minutes * i)).strftime("%Y-%m-%dT%H:%M") for i in range(-steps, steps + 1)]

def create_filename(meta):
    #ts_label = f"{'_'.join(meta['central_timestamp'].split(' '))}"
    return f"label-{meta['label']}_dist-{meta['distance']:.4f}_ul-{meta['ul_lat']:.2f}_{meta['ul_lon']:.2f}_{meta['sample_id']}"

def read_file_from_s3(s3, key):
    try:
        obj = s3.get_object(Bucket=S3_BUCKET_NAME, Key=key)
        return io.BytesIO(obj['Body'].read())
    except Exception as e:
        logging.warning(f"Could not read {key}: {e}")
        return None

def get_dataset_from_timestamps(s3, timestamp_list):
    datasets = []
    for ts in timestamp_list:
        year, month, day = ts[:4], ts[5:7], ts[8:10]
        print(f"Processing timestamp: {ts} for {year}-{month}-{day}")
        key = f"/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN/{year}/{month}/merged_MSG_CMSAF_{year}-{month}-{day}.nc"
        obj = read_file_from_s3(s3, key)
        if not obj:
            continue
        ds = xr.open_dataset(obj)

        if set(CLOUD_PRM).issubset(ds.data_vars):
            #ds_vars = ds[CLOUD_PRM]
            #if APPLY_CMA and 'cma' in ds:
            #    ds_vars = apply_cma_mask(ds, ds_vars, VALUE_MAX[0])
            try:
                ds_filtered = ds.sel(time=ts)
                #print(ds_filtered)
                datasets.append(ds_filtered)
            except KeyError:
                logging.warning(f"Time {ts} not in dataset.")
    
    return xr.concat(datasets, dim="time") if datasets else None

def crop_and_save(ds_crop, ul_lat, ul_lon, meta, outdir):
    os.makedirs(outdir, exist_ok=True)
    filename = create_filename(meta)
    #save_path = os.path.join(outdir, filename)
    crops_nc_fixed(ds_crop, X_PIXEL, Y_PIXEL, [(ul_lat, ul_lon)], filename, outdir)

def main(input_csv, outdir, top_n=10):
    df = pd.read_csv(input_csv)
    #remove invalid labels -100
    df = df[df['label'] != -100]

    s3 = boto3.client(
        's3',
        endpoint_url=S3_ENDPOINT_URL,
        aws_access_key_id=S3_ACCESS_KEY,
        aws_secret_access_key=S3_SECRET_ACCESS_KEY
    )

    for label in df['label'].unique():
        label_df = df[df['label'] == label].nlargest(top_n, 'distance')
        for _, row in label_df.iterrows():
            sample_id = int(row['crop_index'])
            date_str, time_str, lat, lon, grid_size = parse_filename(row['path'])
            print(f"Processing sample {sample_id}: {date_str} {time_str} | Lat: {lat}, Lon: {lon}, Grid Size: {grid_size}")
            timestamp_list = generate_timestamps(date_str, time_str)
            base = datetime.strptime(f"{date_str}T{time_str}", "%Y%m%dT%H:%M")
            print(base)
            #print(f"Generated timestamps for {sample_id}: {len(timestamp_list)}")
            #exit()
            meta = {
                "sample_id": sample_id,
                "label": row["label"],
                "distance": row["distance"],
                "ul_lat": lat,
                "ul_lon": lon,
                "timestamps": timestamp_list,
                "central_timestamp": base
            }

            logging.info(f"Processing sample {sample_id} with timestamps: {timestamp_list[0]} to {timestamp_list[-1]}")
            ds_crop = get_dataset_from_timestamps(s3, timestamp_list)

            if ds_crop is not None:
                crop_and_save(ds_crop, lat, lon, meta, outdir)
            else:
                logging.warning(f"Skipping {sample_id}: No data found.")



if __name__ == "__main__":

    
    general_path = "/data1/fig/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/closest/"
    input_csv_path = f"{general_path}crop_list_dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA_1000_closest.csv"  # Replace with your input CSV file path
    output_csv_path = f"/data1/crops/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/test/centroids_evolution"  # Replace with your desired output CSV file path

    main(input_csv_path, output_csv_path, top_n=10)

#3284240