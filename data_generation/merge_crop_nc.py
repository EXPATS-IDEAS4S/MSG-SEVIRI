import os
import xarray as xr

# Specify the directory containing the NetCDF files
input_directory = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc/'
output_file = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/merged_crops.nc'

# Initialize an empty list to store the Datasets
datasets = []

# Loop through all NetCDF files in the directory
for filename in sorted(os.listdir(input_directory)):
    if filename.endswith('.nc'):
        # Construct the full path to the file
        file_path = os.path.join(input_directory, filename)
        
        # Load the NetCDF file
        ds = xr.open_dataset(file_path)
        
        # Append the Dataset to the list
        datasets.append(ds)

# Concatenate all Datasets along the time dimension
merged_ds = xr.concat(datasets, dim='time')

# Save the merged dataset to a new NetCDF file
merged_ds.to_netcdf(output_file)

print(f"Successfully merged {len(datasets)} files into {output_file}")