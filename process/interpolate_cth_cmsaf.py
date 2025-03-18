"""
Open MSG-SEVIRI files with Satpy 
Crop it to area of interest, 
project it in latlon grid 
and convert it to netCDF
if needed perfrom parallax correction
and regrid the data in a regular lat-lon grid

@author: Daniele Corradini

TODO: check for missing timestamps once the daily dataset has been created
TODO: better handle inizialization of dataset for native grid 
"""
# %%
from glob import glob
import xarray as xr
from datetime import datetime, timedelta
import os
import time
import numpy as np
import warnings
import matplotlib.pyplot as plt
import pandas as pd


#Import parameters from config file and custom methods
from MSG_preprocess_satpy import get_datetime_cth, compute_timestamps_from_time_range
from config_satpy_process import path_to_file, path_to_cth, natfile, cth_file, path_to_save
from config_satpy_process import lonmin, lonmax, latmax, latmin, channels, step_deg, interp_method
from config_satpy_process import parallax_correction, regular_grid, msg_res, cth_res
from config_satpy_process import msg_reader, cth_reader
from config_satpy_process import year, month
from regrid_functions import regrid_data, fill_missing_data_with_interpolation, generate_regular_grid

# get path of this file
dir_path = os.path.dirname(os.path.abspath(__file__))

all_cth_vars = ['ctt', 'ctp', 'ctth_alti', 'conditions', 'quality', 
            'status_flag', 'ctt_unc', 'cth_unc', 'ctp_unc', 'record_status', 
            'platform_flag', 'subsatellite_lon', 'subsatellite_lat', 
            'subsatellite_alt', 'georef_offset_corrected', 'projection']

# %%
# get all cth files from path
year = 2022
start_date=f"{year}.06.05" # <<<<<<<<<<<<<<<<<<<
end_date=f"{year}.06.06" # <<<<<<<<<<<<<<<<<<< (excluding)
# new resolution
interpol_res = 5
interpol_method = "linear"
output_folder = f"{path_to_cth[:-1]}_interpolated_{interpol_res}min"
os.makedirs(output_folder, exist_ok=True)

def generate_interpolated_CTH_timestamps(year, start_date, end_date, output_folder, interpol_res=5, interpol_method='linear'):

    # get all cth timestamps in this period
    timestamps = compute_timestamps_from_time_range(start_date, end_date)
    print(len(timestamps), timestamps[0], timestamps[-1])

    # get all unique days in this list to loop over respective folders
    unique_days = np.unique(pd.to_datetime(timestamps).date)

    # get all cth files in this period
    cth_files = []
    for day in unique_days:
        # collect all cth files of this day
        day_files = sorted(glob(os.path.join(path_to_cth, f"{day.year}/{day.month:02d}/{day.day:02d}/{cth_file}")))
        # check if last unique day (end of period)
        if day == unique_days[-1]:
            # write only first file to list
            cth_files.extend([day_files[0]])
        else:
            # write to list
            cth_files.extend(day_files)
    
def get_filename_for_interpolated_timestamps(cth_file, time_step, time_interval=5, interpol='linear'):
    # get filename without extension
    f = os.path.basename(cth_file).split('.')[0]
    # replace minutes in filename by current (interpolated) timestamp
    f = f[:15] + f"{int(f[15:17])+time_step*time_interval:02d}" + f[17:]
    # add interpolation method and extension
    return f"{f}_interpol{interpol}.nc"

# %%
def interpolate_and_save(cth_files, var='ctth_alti', time_interval=5, interpol='linear', plot_path=None):
    # create subfolder for different interpolation method
    out_path = os.path.join(output_folder, interpol)
    os.makedirs(out_path, exist_ok=True)

    # loop over cth files
    count_missing = 0
    for f, cthfile in enumerate(cth_files[:-1]):
        previous_file = cthfile
        following_file = cth_files[f+1]

        # check if the files are consecutive
        dt_previous = get_datetime_cth(os.path.basename(previous_file))
        dt_following = get_datetime_cth(os.path.basename(following_file))
        if dt_following - dt_previous != timedelta(minutes=15):
            print(f"Skipping {previous_file} because the consecutive timestamp is missing.")
            count_missing += 1
            continue

        # open the files
        drop_vars = [x for x in all_cth_vars if x != var]
        with xr.open_mfdataset([previous_file, following_file], drop_variables=drop_vars) as data:
            data_xarray = data
        
        # interpolate to 5 minutes timestamps
        data_resampled = data_xarray.resample(time=f'{time_interval}T').interpolate(kind=interpol)

        # save each interpolated timestamp in a separate file
        for t, timestamp in enumerate(data_resampled.time.values):
            dt =  pd.to_datetime(timestamp)

            # to save only the interpolated timestamps - continue if dt is original timestamp
            if dt == dt_previous or dt == dt_following:
                continue
            
            # create folder if it does not exist
            folder = os.path.join(out_path, f"{dt.year}/{dt.month:02d}/{dt.day:02d}")
            os.makedirs(folder, exist_ok=True)

            # get output file name
            out_name = get_filename_for_interpolated_timestamps(cthfile, t, time_interval=time_interval, interpol=interpol)
            
            # save file
            data_resampled[var][t].to_netcdf(os.path.join(folder, out_name))
            # CTXin20220930114500405SVMSGI1UD.nc
        
        # if plot_path is not None:
        #     # create subplots for each timestamp
        #     fig, axes = plt.subplots(1, len(data_resampled.time), figsize=(10, 3))
        #     fig.suptitle(interpol)
        #     # loop over timestamps and plot the data
        #     for t in range(len(data_resampled.time)):
        #         # time stamp
        #         dt =  pd.to_datetime(data_resampled.time[t].values)

        #         # Get hour and minute
        #         hour = dt.hour
        #         minute = dt.minute
        #         # plot in subplot
        #         ax = axes[t]
        #         ax.set_title(f"{hour:02d}:{minute:02d}")
        #         # plot the data
        #         ax.imshow(data_resampled[var][t].values[-50:, -50:], origin='lower', vmin=0, vmax=15000)
        #         # data_resampled[var][t].plot()
        #     plt.savefig(os.path.join(plot_path, f"{interpol}_{dt.strftime('%Y%m%d_%H%M')}.png"))
        #     plt.show()
        #     plt.close()

# %%
interpolate_and_save(cth_files, var='ctth_alti', time_interval=5, interpol='linear')


# %%start = data_xarray.time.values[0]
end = data_xarray.time.values[-1]
print(start, end, start<end)
# ts_new = compute_timestamps_from_time_range(start, end, time_interval=5)
# print(ts_new)
# create subplots for each timestamp
fig, axes = plt.subplots(1, len(data_xarray.time), figsize=(10, 3))
# loop over timestamps and plot the data
for t in range(len(data_xarray.time)):
    # time stamp
    dt =  pd.to_datetime(data_xarray.time[t].values)

    # Get hour and minute
    hour = dt.hour
    minute = dt.minute
    # plot in subplot
    ax = axes[t]
    ax.set_title(f"{hour:02d}:{minute:02d}")
    # plot the data
    ax.imshow(data_xarray[var][t].values[-50:, -50:], origin='lower', vmin=0, vmax=15000)
    # data_resampled[var][t].plot()
plt.show()
plt.close()

# %%
methods = ['linear', 'nearest']

for method in methods:
    print(method)
    if method != 'polynomial':
        data_resampled = data_xarray.resample(time='5T').interpolate(kind=method)
    else:
        data_resampled = data_xarray.resample(time='5T').interpolate(kind='polynomial', order=3)
    

