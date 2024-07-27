import xarray as xr
import pandas as pd
import os
from glob import glob
import numpy as np

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
        total = counts.sum()
        for u, c in zip(unique, counts):
            stats[f"{variable}_category_{u}_percentage"] = (c / total) * 100
    else:
        percentiles = [1, 25, 50, 75, 99]
        for p in percentiles:
            stats[f"{variable}_percentile_{p}"] = np.percentile(data, p)
    
    return stats

def process_crop_files(MSG_crops_list, cloud_crops_list, output_csv):
    """
    Process crop files to compute statistics for cloud properties and IR channel.
    #TODO improve in case the MSG crops include more that one channel
    #TODO Get the variables name from inpute

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
    
    for i, crop_file in enumerate(cloud_crops_list):
        crop_ds = xr.open_dataset(crop_file, decode_times=True)
        stats = {"filename": os.path.basename(crop_file)}

        # Compute statistics for categorical variables
        categorical_vars = ['cph', 'cma']
        for var in categorical_vars:
            if var in crop_ds.data_vars:
                stats.update(compute_statistics(crop_ds, var, is_categorical=True))

        # Compute statistics for continuous variables
        continuous_vars = ['cwp', 'cot', 'ctt', 'ctp', 'cth'] #TDO ad cre
        for var in continuous_vars:
            if var in crop_ds.data_vars:
                stats.update(compute_statistics(crop_ds, var, is_categorical=False))

        #compute statistics for the MSG channel
        MSG_ds = xr.open_dataset(MSG_crops_list[i], decode_times=True) 
        stats.update(compute_statistics(MSG_ds, 'IR_108', is_categorical=False))    

        results.append(stats)
    
    # Convert results to DataFrame and save to CSV
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False)
    print(f"Saved statistics to {output_csv}")

# Define directories
cloud_crop_directory = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc_clouds/'
MSG_crop_directory = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc/'
output_csv = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/crops_stats.csv'

# Get list of crop files
cloud_crops_list = sorted(glob(f'{cloud_crop_directory}*.nc'))
MSG_crops_list = sorted(glob(f'{MSG_crop_directory}*.nc'))

if len(MSG_crops_list)== len(cloud_crops_list):
    # Process the crop files and save the statistics
    process_crop_files(MSG_crops_list, cloud_crops_list, output_csv)
else:
    print('something wrong with the number of files')
