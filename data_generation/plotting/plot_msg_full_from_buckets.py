import os
import io
import boto3
import logging
from botocore.exceptions import ClientError
import xarray as xr
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from scipy.ndimage import binary_closing
import numpy as np
import pandas as pd
from matplotlib.colors import ListedColormap

import sys

sys.path.append('/home/Daniele/codes/MSG-SEVIRI/data_generation/')

from cropping_functions import crops_nc_random, crops_nc_fixed, filter_by_domain, filter_by_time
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

# # List the objects in our bucket
# response = s3.list_objects(Bucket=S3_BUCKET_NAME)
# for item in response['Contents']:
#     print(item['Key'])


#Directory with the data to uplad
years = [2024]
months = range(8,9)
days = range(1,2)
path_dir = f"/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN"
basename = "merged_MSG_CMSAF"
 

domain = lonmin, lonmax, latmin, latmax = 5, 16, 42, 51.5 #DC domain from the paper
domain_name = 'EXPATS'

cloud_prm = ['IR_108', 'WV_062', 'cma']

#colormaps
cma_cmap = ListedColormap(["black", "white"])
ir108_cmap = plt.cm.Greys
wv062_cmap = plt.cm.Greys
ir108_norm = plt.Normalize(vmin=200, vmax=300)
wv062_norm = plt.Normalize(vmin=200, vmax=300)


#output_path =  f'/work/dcorradi/crops/{cloud_prm_str}_{years_str}_{x_pixel}x{y_pixel}_{domain_name}_{cropping_strategy}/'
outpath = '/sat_data/crops/msg_full_expats_domain/'
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
                ds_day = xr.open_dataset(io.BytesIO(my_obj), engine='h5netcdf')
                #print(ds_day)
                
                
                #select only variable of interest
                ds_day = ds_day[cloud_prm]         

                #select only data within certain domain
                try:
                    ds_day = filter_by_domain(ds_day, domain)
                except ValueError as e:
                    print(f"Skipping file '{file}' due to error: {e}")
                    continue  # Skip this file and move to the next

                #extract timestamp
                timestamps = ds_day.time.values
                #print(timestamps)

                #loop through each daily file
                for timestamp in timestamps:
                    #extract hour
                    hour = str(timestamp).split('T')[1][0:2]
                    #print(hour)
                    #print(month)
                
                    #select the values for the current timestamp
                    try:
                        ds_time = filter_by_time(ds_day,timestamp)
                    except ValueError as e:
                        print(f"Skipping file '{file}-{timestamp}' due to error: {e}")
                        continue  # Skip this file and move to the next
                     

                    # saving cropped images
                    filename_to_save = file.split('/')[-1].split('.')[0]+'_'+str(timestamp).split('T')[1][0:5]+'_'+domain_name
                    print(filename_to_save)

                    
                    # -------------------------
                    # output directory
                    # -------------------------

                    year_str = f"{pd.Timestamp(timestamp).year:04d}"
                    month_str = f"{pd.Timestamp(timestamp).month:02d}"
                    day_str = f"{pd.Timestamp(timestamp).day:02d}"

                    outdir = os.path.join(
                        outpath,
                        year_str,
                        month_str,
                        day_str
                    )

                    os.makedirs(outdir, exist_ok=True)

                    outfile = os.path.join(
                        outdir,
                        f"{filename_to_save}.png"
                    )

                    # -------------------------
                    # data
                    # -------------------------

                    ir108 = ds_time["IR_108"].isel(time=0)
                    wv062 = ds_time["WV_062"].isel(time=0)

                    # replace with actual CMA variable name
                    cma = ds_time["cma"].isel(time=0)
                    #apply closing alorithm with closing 3x3 to the cma variable
                    cma = cma.fillna(0) #replace NaN with 0
                    cma = cma.astype(int) #convert to integer
                    cma_closed = cma.copy()
                    
                    cma_closed.values = binary_closing(cma.values, structure=np.ones((3,3)))

                    lons = ds_time.lon
                    lats = ds_time.lat

                    # -------------------------
                    # plot
                    # -------------------------

                    fig, axs = plt.subplots(
                        1,
                        3,
                        figsize=(18, 6),
                        subplot_kw={"projection": ccrs.PlateCarree()}
                    )

                    plots = [
                        (ir108, "IR 10.8 µm", "Greys", ir108_norm),
                        (wv062, "WV 6.2 µm", "Greys", wv062_norm),
                        (cma_closed, "Cloud Mask (Closed)", cma_cmap, None),
                    ]

                    for ax, (field, title, cmap, norm) in zip(axs, plots):

                        ax.set_extent(
                            [
                                float(lons.min()),
                                float(lons.max()),
                                float(lats.min()),
                                float(lats.max())
                            ],
                            crs=ccrs.PlateCarree()
                        )

                        ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
                        ax.add_feature(cfeature.BORDERS, linewidth=0.5)

                        pcm = ax.pcolormesh(
                            lons,
                            lats,
                            field,
                            cmap=cmap,
                            norm=norm,
                            shading="auto",
                            transform=ccrs.PlateCarree()
                        )

                        ax.set_title(title)

                        plt.colorbar(
                            pcm,
                            ax=ax,
                            orientation="horizontal",
                            pad=0.03,
                            shrink=0.8
                        )

                    fig.suptitle(
                        pd.Timestamp(timestamp).strftime("%Y-%m-%d %H:%M UTC"),
                        fontsize=16, y=1.05, fontweight='bold'
                    )

                    plt.tight_layout()

                    plt.savefig(
                        outfile,
                        dpi=200,
                        bbox_inches="tight"
                    )

                    plt.close()
                    
                    
                    
                   
                    

