import os
import xarray as xr
import numpy as np
from scipy import interpolate

# Root folder with .nc files
root_folder = '/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nc'

# Loop over all subfolders
for subdir, dirs, files in os.walk(root_folder):
    for file in files:
        if file.endswith('.nc'):
            file_path = os.path.join(subdir, file)
            print(f"Processing file: {file_path}")
            
            try:
                ds = xr.open_dataset(file_path, engine='h5netcdf')
                # Assuming variable name is the first one
                var_name = list(ds.data_vars)[0]
                data = ds[var_name].values
                shape = data.shape
                
                # Check if there's a time dimension
                if 'time' in ds[var_name].dims:
                    time_dim = ds[var_name].dims.index('time')
                else:
                    time_dim = None
                
                # Flag to track if any timestep has >5% NaNs
                delete_file = False
                modified = False
                
                if time_dim is not None:
                    for t in range(data.shape[time_dim]):
                        slice_data = data[t, :, :]
                        nan_count = np.isnan(slice_data).sum()
                        total_pixels = slice_data.size
                        
                        if nan_count > 0:
                            if nan_count / total_pixels > 0.05:
                                print(f"Time step {t}: {nan_count}/{total_pixels} NaNs (>5%), deleting file!")
                                delete_file = True
                                break  # No need to check further timesteps
                            else:
                                # Interpolate using nearest neighbor
                                x, y = np.meshgrid(np.arange(slice_data.shape[1]), np.arange(slice_data.shape[0]))
                                valid_mask = ~np.isnan(slice_data)
                                interpolator = interpolate.NearestNDInterpolator(
                                    list(zip(x[valid_mask], y[valid_mask])),
                                    slice_data[valid_mask]
                                )
                                slice_data_filled = interpolator(x, y)
                                data[t, :, :] = slice_data_filled
                                modified = True
                else:
                    # 2D file without time
                    slice_data = data
                    nan_count = np.isnan(slice_data).sum()
                    total_pixels = slice_data.size
                    if nan_count / total_pixels > 0.05:
                        print(f"File {file_path} has >5% NaNs, deleting file!")
                        delete_file = True
                    elif nan_count > 0:
                        x, y = np.meshgrid(np.arange(slice_data.shape[1]), np.arange(slice_data.shape[0]))
                        valid_mask = ~np.isnan(slice_data)
                        interpolator = interpolate.NearestNDInterpolator(
                            list(zip(x[valid_mask], y[valid_mask])),
                            slice_data[valid_mask]
                        )
                        data = interpolator(x, y)
                        modified = True
                
                ds.close()
                
                # Delete the file if necessary
                if delete_file:
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                elif modified:
                    # Reopen and save interpolated data
                    ds = xr.open_dataset(file_path, mode='a', engine='h5netcdf')
                    ds[var_name].values = data
                    ds.to_netcdf(file_path, engine='h5netcdf')
                    ds.close()
                    print(f"Updated file: {file_path}")
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
