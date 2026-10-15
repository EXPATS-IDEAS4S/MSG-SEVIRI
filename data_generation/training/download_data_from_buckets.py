import os
import boto3
import logging
from botocore.exceptions import ClientError
from datetime import datetime
import sys

sys.path.append('/home/Daniele/codes/MSG-SEVIRI/data_generation/')
from credentials_buckets import S3_ACCESS_KEY, S3_SECRET_ACCESS_KEY, S3_ENDPOINT_URL

S3_BUCKET_NAME = 'expats-radar-germany'

s3 = boto3.client(
    's3',
    endpoint_url=S3_ENDPOINT_URL,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_ACCESS_KEY
)

outpath = '/data1/other_data/radolan'
os.makedirs(outpath, exist_ok=True)

years = [2023]
months = range(4, 10)
days = range(1, 32)

for year in years:
    for month in months:
        for day in days:
            #prefix = f"output/data/timeseries_crops/{year:04d}/{month:02d}/{day:02d}/MSG_timeseries_{year:04d}-{month:02d}-{day:02d}_"
            prefix = f"/net/ostro/radolan_5min_composites/{year}{month:02d}{day:02d}_RR_15min_msg_res.nc" #f"/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN/{year}/{month:02d}/merged_MSG_CMSAF_{year}-{month:02d}-{day:02d}.nc"
            try:
                response = s3.list_objects_v2(
                    Bucket=S3_BUCKET_NAME,
                    Prefix=prefix
                )
                if "Contents" not in response:
                    print(f"No files for {year}-{month:02d}-{day:02d}")
                    continue

                for obj in response["Contents"]:
                    key = obj["Key"]
                    if not key.endswith(".nc"):
                        continue

                    filename = os.path.basename(key)
                    local_file = os.path.join(outpath, filename)

                    if os.path.exists(local_file):
                        print(f"Already downloaded: {filename}")
                        continue

                    print(f"Downloading: {key}")
                    with open(local_file, "wb") as f:
                        s3.download_fileobj(S3_BUCKET_NAME, key, f)

            except ClientError as e:
                print(f"Failed to list/download files for {year}-{month:02d}-{day:02d}: {e}")