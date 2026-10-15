import os
import shutil
import xarray as xr
import numpy as np

# Root folder with .nc files
root_folder = '/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nc'

# Folder to move NaN-containing files
quarantine_folder = '/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nc_with_nans'

# Create quarantine folder if it does not exist
os.makedirs(quarantine_folder, exist_ok=True)

# Loop over all subfolders
for subdir, dirs, files in os.walk(root_folder):
    for file in files:
        if file.endswith('.nc'):
            file_path = os.path.join(subdir, file)
            print(f"Checking file: {file_path}")
            
            try:
                ds = xr.open_dataset(file_path,engine='h5netcdf')
                var_name = list(ds.data_vars)[0]  # assuming the main variable
                data = ds[var_name].values
                
                if np.isnan(data).any():
                    ds.close()
                    dest_path = os.path.join(quarantine_folder, file)
                    shutil.move(file_path, dest_path)
                    print(f"Moved file with NaNs to quarantine: {dest_path}")
                else:
                    ds.close()
                    
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
