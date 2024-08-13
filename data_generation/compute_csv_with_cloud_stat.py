import xarray as xr
import pandas as pd
import os
from glob import glob
import numpy as np
import random
import time

def find_corresponding_file(cloud_list, target_time):
    """
    Find the corresponding cloud file based on the timestamp.

    Parameters:
    -----------
    cloud_list : list of str
        List of file paths to the cloud properties NetCDF files.
    target_time : numpy.datetime64
        The timestamp for which the corresponding cloud file is needed.

    Returns:
    --------
    str or None
        The file path of the corresponding cloud file if found, otherwise None.
    """
    for filename in cloud_list:
        ds = xr.open_dataset(filename, decode_times=True)
        if 'time' in ds.coords and target_time in ds['time'].values:
            return filename
    return None


def process_files(crop_file, cloud_list, output_dir=None):
    """
    Process IR and cloud physical properties files to combine the data.

    Parameters:
    -----------
    crops_list : list of str
        List of file paths to the crop (IR) NetCDF files.
    cloud_list : list of str
        List of file paths to the cloud properties NetCDF files.
    output_dir : str
        Directory where the combined output files will be saved.

    Returns:
    --------
    None
    """
    #for crop_file in crops_list:
    crop_ds = xr.open_dataset(crop_file, decode_times=True)
    #print(crop_ds)

    # Get the time from the IR file
    crop_time = crop_ds['time'].values[0]
    print(crop_time)

    # Find the corresponding cloud file based on the time
    cloud_filepath = find_corresponding_file(cloud_list, crop_time)
    if cloud_filepath is None:
        print(f"No matching cloud file found for time: {crop_time}")
        return None

    cloud_ds = xr.open_dataset(cloud_filepath, decode_times=True)
    #print(cloud_ds)

    # Select the data within the lat/lon bounds of the IR data
    lat_bounds = crop_ds['lat'].values[[0, -1]]
    lon_bounds = crop_ds['lon'].values[[0, -1]]
    #print(lat_bounds, lon_bounds)

    #TODO try to include the same amount of pixels, maybe slice not proper or regrid didn't work?
    cloud_ds_sel = cloud_ds.sel(
        lat=slice(lat_bounds[0], lat_bounds[1]),
        lon=slice(lon_bounds[0], lon_bounds[1]),
        time=crop_time
    )

    if output_dir:
        #output_filename = crop_file
        output_filepath = output_dir+crop_file.split('/')[-1]
        #print(output_filepath)

        # Save the combined dataset to a new NetCDF file
        cloud_ds_sel.to_netcdf(output_filepath)
        print(f"Saved combined dataset to {output_filepath}")
    else:
        return cloud_ds_sel

def compute_statistics(dataset, variable, is_categorical):
    """
    Compute statistics for a given variable in the dataset.

    Parameters:
    -----------
    dataset : xarray.Dataset
        The dataset containing the variable to be analyzed.
    variable : str
        The name of the variable to analyze.
    is_categorical : bool
        Whether the variable is categorical or continuous.

    Returns:
    --------
    dict
        A dictionary containing the computed statistics.
    """
    data = dataset[variable].values.flatten()
    stats = {}
    
    if is_categorical:
        unique, counts = np.unique(data, return_counts=True)
        #print(unique, counts)
        total = counts.sum()
        for u, c in zip(unique, counts):
            stats[f"{variable}_category_{int(u)}_percentage"] = (c / total)*100
            #print(np.round((c / total)*100,2))
    else:
        percentiles = [1, 25, 50, 75, 99]
        for p in percentiles:
            data = data[~np.isnan(data)]
            if len(data)>0:
                stats[f"{variable}_percentile_{p}"] = np.percentile(data, p)
            else:
                stats[f"{variable}_percentile_{p}"] = np.nan
    
    return stats

def process_crop_files(MSG_crops_list, cloud_list, output_csv, categorical_vars, continuous_vars, msg_vars):
    """
    Process crop files to compute statistics for cloud properties and IR channel.
    #TODO improve the speed, maybe parallel process?


    Parameters:
    -----------
    crops_list : list of str
        List of file paths to the crop (IR) NetCDF files.
    output_csv : str
        Path to the output CSV file to save the statistics.

    Returns:
    --------
    None
    """
    results = []
    
    for i, crop_file in enumerate(MSG_crops_list):
        crop_ds = process_files(crop_file, cloud_list, output_dir=None)
        if crop_ds:
            stats = {"filename": os.path.basename(crop_file)}

            # Compute statistics for categorical variables
            for var in categorical_vars:
                if var in crop_ds.data_vars:
                    stats.update(compute_statistics(crop_ds, var, is_categorical=True))

            # Compute statistics for continuous variables
            for var in continuous_vars:
                if var in crop_ds.data_vars:
                    stats.update(compute_statistics(crop_ds, var, is_categorical=False))

            #compute statistics for the MSG channel
            MSG_ds = xr.open_dataset(MSG_crops_list[i], decode_times=True) 
            for var in msg_vars:
                if var in MSG_ds.data_vars:
                    stats.update(compute_statistics(MSG_ds, var, is_categorical=False))    

            results.append(stats)
            #print(results)
            #exit()
    
    # Convert results to DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Saved statistics to {output_csv}")


# Start time
begin_time = time.time()

# Define directories
crop_directory = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc/' #70135?
cloud_directory = '/data/sat/msg/CM_SAF/merged_cloud_properties/2013/'

categorical_vars = ['cph', 'cma']
continuous_vars = ['cwp', 'cot', 'cre', 'ctt', 'ctp', 'cth']
msg_vars = ['IR_108']#, 'IR_039', 'WV_062']

#get list of cloud properties files and crop files
msg_crops_list = sorted(glob(f'{crop_directory}*.nc'))
#print(crops_list)
clouds_list = sorted(glob(f'{cloud_directory}*/*.nc'))
#print(clouds_list)

# Specify the number of samples you want to take
num_samples = 5000  

output_csv = f'/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/crops_stats_{str(num_samples)}.csv'

# Take a random sample from the list of cros
random_sample_crop_list = random.sample(msg_crops_list, num_samples)

process_crop_files(random_sample_crop_list, clouds_list, output_csv, categorical_vars, continuous_vars, msg_vars)


# End time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - begin_time

print(f"Elapsed time for computing {str(num_samples)}: {elapsed_time} seconds")

   

#nohup 1477336

#Elapsed time for computing 1000: 6614.142078876495 seconds, 13h circa for 5000 crops -> parallelization!