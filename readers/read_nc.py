import netCDF4 as nc
import xarray as xr
from glob import glob
import numpy as np

# Path to your NetCDF file
#path_to_files = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/'
#nc_file = 'CTXin20210712000000405SVMSGI1UD.nc'
path_to_files = "/data/sat/msg/orography/"
nc_file = 'adaptor.mars.internal-1727169276.6659045-21410-8-f318c7b8-e965-4ae1-aaa3-b8fc8b702570.nc'
ds = xr.open_dataset(path_to_files+nc_file)
print(ds)
#print(ds.lat.values, ds.lon.values)
#print(ds.lons.values.flatten()[1000:])
#print(ds.lats.values.flatten()[1000:])

exit()

# Define the bounding box for cropping (latmin, latmax, lonmin, lonmax)
latmin, latmax = 42, 51.5
lonmin, lonmax = 5, 16

# Crop the dataset using sel() by specifying the latitude and longitude bounds
cropped_ds = ds.sel(lat=slice(latmin-0.1, latmax+0.1), lon=slice(lonmin-0.1, lonmax+0.1))

# Save the cropped dataset if necessary
cropped_ds.to_netcdf("/data/sat/msg/orography/IMERG_landseamask_EXPATS_0.1x0.1.nc")

# Print a summary of the cropped dataset to check
print(cropped_ds)




fnames = sorted(glob(path_to_files+nc_file))
print(fnames)

for file in fnames:

    ds = xr.open_dataset(file)
    #ds = xr.open_mfdataset(fnames, combine='nested', concat_dim='time', parallel=True)
    print(ds.cma.values)
#print(ds.cre.values)
# print(ds.cot.values)
# print(np.unique(ds.cph.values))
# print(ds.cwp.values) #0,1,2 cloud free, liquid, ice
# print(ds.ctt.values)
# print(ds.ctp.values)
# print(ds.cth.values)
# print(np.unique(ds.cma.values)) #0, 1, clear, cloudy
#print(ds.cma)



# # Open the NetCDF file
# dataset = nc.Dataset(path_to_files+nc_file, 'r')  # 'r' is for read mode

# # Accessing global attributes
# print("Global attributes:")
# for attr in dataset.ncattrs():
#     print(f"{attr}: {getattr(dataset, attr)}")

# # Accessing dimensions
# print("\nDimensions:")
# for dim in dataset.dimensions.values():
#     print(dim)

# # Accessing variables
# print("\nVariables:")
# for var in dataset.variables:
#     print(f"{var}: {dataset.variables[var]}")




# # Example of reading data from a variable
# # Replace 'your_variable_name' with the actual variable name you want to access
# variable_name = 'your_variable_name'
# if variable_name in dataset.variables:
#     variable_data = dataset.variables[variable_name][:]
#     print(f"\nData for {variable_name}:")
#     print(variable_data)
# else:
#     print(f"Variable {variable_name} not found in the file.")


# Close the dataset
# dataset.close()
