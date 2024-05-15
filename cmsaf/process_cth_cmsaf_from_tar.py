"""
Processing CTH data from CMSAF to make it compatible with Satpy for the parallax correction
and downloading data directly into the specified directory structure.

@author: Daniele Corradini
"""

import xarray as xr
import os
import subprocess
from glob import glob

### Define Paths and Variables ###
year = '2023'
base_url = "https://cmsaf.dwd.de/data/ORD55029/"
username = "routcm"
password = "4gVdHUdpq8UhHcIJIP"

# Base path where CTH data are stored and output path
path_to_files = f'/data/sat/msg/CM_SAF/CTH/{year}/'
path_out = f'/data/sat/msg/CM_SAF/CTH/{year}/'

# Wget and tar extraction command
wget_command = [
    "wget", "-r", "-np", "-nH", "--cut-dirs=1", "--reject=index.html",
    "--user", username, "--password", password, base_url
]
subprocess.run(wget_command, check=True)

# Find tar files and unpack them
tar_files = sorted(glob(path_to_files + "*.tar"))
for tar_file in tar_files:
    tar_command = ["tar", "-xvf", tar_file, "-C", path_to_files]
    subprocess.run(tar_command, check=True)
    os.remove(tar_file)  # Remove the tar file after extraction

# Process extracted NC files
nc_file_pattern = "CTX*.nc"
fnames = sorted(glob(path_to_files + "**/" + nc_file_pattern, recursive=True))

# Read and process CTH data
for f in fnames:
    print(f.split('/')[-1])
    # Extract date and time from filename
    time_str = f.split('/')[-1].split('.')[0][5:13]
    month, day = time_str[4:6], time_str[6:8]

    ### Open and process NetCDF data ###
    ds_cth_cmsaf = xr.open_dataset(f)
    ds_cth_cmsaf = ds_cth_cmsaf.rename({'cth': 'ctth_alti'})
    
    # Assign satellite parameters
    ds_cth_cmsaf['ctth_alti'].attrs.update({
        'satellite_nominal_latitude': ds_cth_cmsaf.subsatellite_lat.values[0],
        'satellite_nominal_longitude': ds_cth_cmsaf.subsatellite_lon.values[0],
        'satellite_nominal_altitude': ds_cth_cmsaf.subsatellite_alt.values[0]
    })

    filename_save = f.split('/')[-1]
    path_output = os.path.join(path_out, month, day)

    if not os.path.exists(path_output):
        os.makedirs(path_output)

    # Save processed data
    ds_cth_cmsaf.to_netcdf(os.path.join(path_output, filename_save))
    ds_cth_cmsaf.close()  # Close the dataset
    print(f"File {filename_save} saved at {path_output}")





        




    
