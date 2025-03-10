import os
import xarray as xr
from glob import glob

years = [2016, 2017, 2018]
months = range(4,10)
variables_msg = ['IR_108', 'WV_062']
variables_cmsaf = ['cma']

base_sat_path = "/data/sat/msg/netcdf/parallax"
base_cma_path = "/data/sat/msg/CM_SAF/merged_cloud_properties"
target_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN"


for year in years:
    for month in months:  # Loop over months
        # Define file paths
        sat_filepattern = f"{base_sat_path}/{year:04d}/{month:02d}/*.nc"
        cma_filepattern = f"{base_cma_path}/{year:04d}/{month:02d}/*.nc"

        # Find files
        sat_file_list = sorted(glob(sat_filepattern))
        cma_file_list = sorted(glob(cma_filepattern))

        if len(sat_file_list) != len(cma_file_list):
            print(f"Skipping {year}-{month:02d}: Number of files do not match")
            continue
        
        for msg_file, cmsaf_file in zip(sat_file_list, cma_file_list):
            #Get the date from the filename
            date = cmsaf_file.split("/")[-1].split("_")[1]
            print(date)
            
            save_dir = f"{target_path}/{year:04d}/{month:02d}"
            save_path = f"{save_dir}/merged_MSG_CMSAF_{date}.nc"

            if not os.path.exists(save_dir):
                os.makedirs(save_dir, exist_ok=True)

            # Load datasets and 
            ds_sat = xr.open_dataset(msg_file)[variables_msg]
            ds_cma = xr.open_dataset(cmsaf_file)[variables_cmsaf]

            # Convert lat lon coord in float32
            ds_cma['lat'] = ds_cma['lat'].astype('float32')
            ds_cma['lon'] = ds_cma['lon'].astype('float32')

            #Sobstitute ds_sat lat and lon with the one from ds_cma
            ds_sat['lat'] = ds_cma['lat']
            ds_sat['lon'] = ds_cma['lon']

            #convert variable cma in int16
            if 'cma' in variables_cmsaf:
                ds_cma['cma'] = ds_cma['cma'].astype('int16')

            # Merge datasets
            ds_merged = xr.merge([ds_sat, ds_cma])

            # Save merged dataset in a zippered netcdf file
            encoding_dict = {}
            for channel in ds_merged.data_vars:
                encoding_dict[channel] = {"zlib": True, "complevel": 9}
            encoding_dict['time'] = {"units": "seconds since 2000-01-01", "dtype": "i4"}

            # Save the dataset with specified compression settings
            ds_merged.to_netcdf(save_path,encoding=encoding_dict)
            print(f"Saved merged file: {save_path}")

#nohup 3808828