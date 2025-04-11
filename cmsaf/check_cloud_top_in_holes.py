import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from glob import glob
import os
import xarray as xr
import cartopy.crs as ccrs
import numpy as np 
from scipy.interpolate import griddata

def fill_missing_data_with_interpolation(lat, lon, data, method='nearest'):
    """
    Fill missing data in a 2D array using interpolation.

    Parameters:
    - lat: 2D array of latitude values
    - lon: 2D array of longitude values
    - data: 2D array of data with NaN values to fill
    - method: Interpolation method ('linear', 'nearest', etc.)

    Returns:
    - 2D array with interpolated values or None if not enough points
    """
    # Flatten the arrays for processing
    valid_mask = ~np.isnan(data)
    valid_lat = lat[valid_mask]
    valid_lon = lon[valid_mask]
    valid_data = data[valid_mask]

    # Check if there are enough valid points
    if len(valid_data) < 10:
        print("Not enough valid points for interpolation. Skipping.")
        return None  # Indicate a problem with insufficient points

    # Perform interpolation
    filled_data = griddata((valid_lat, valid_lon), valid_data, (lat, lon), method=method)
    return filled_data

cmsaf_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/"
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"
# Open csv file as dataframe
df = pd.read_csv(f'{output_path}cloud_mask_closed_points_flags.csv')
#df = df.apply(pd.to_numeric, errors='ignore', downcast='integer')

#select only rows with structure 3x3
df = df[df['structure'] == '3x3']
tot_rows = len(df)
print(tot_rows)

# Keep only time lot lan xolumns
df = df[['time', 'lat', 'lon']]
print(df)


# Get the list of the nc file in cmsaf_path
nc_files = sorted(glob(os.path.join(cmsaf_path, "2013*.nc")))
print(len(nc_files))

cmsaf_vars = ["ctp", "cot"]

# Initialize new columns in the DataFrame for each variable
for cmsaf_var in cmsaf_vars:
    df[f"{cmsaf_var}_value"] = np.nan  # Placeholder for original values
    df[f"{cmsaf_var}_regridded"] = np.nan  # Placeholder for regridded values

# Loop over the DataFrame rows
for index, row in df.iterrows():
    #print(row)
    time = row['time']
    lat = row['lat']
    lon = row['lon']
    print(time, lat, lon)
    
    # Convert time to datetime and extract components
    time = pd.to_datetime(time)
    year, month, day, hour, minute = time.year, time.month, time.day, time.hour, time.minute
    
    # Construct file path
    cloud_nc = f"{cmsaf_path}{year}{month:02d}{day:02d}_{hour:02d}:{minute:02d}_EXPATS_0.nc"
    print(cloud_nc)
    
    # Check if the file exists
    if not os.path.exists(cloud_nc):
        continue
    
    # Open the NetCDF file
    cloud_ds = xr.open_dataset(cloud_nc)
    
    # Loop over each variable in cmsaf_vars
    for cmsaf_var in cmsaf_vars:
        # Extract the variable from the dataset
        cloud_ds_var = cloud_ds[cmsaf_var]
        
        # Get latitude and longitude arrays
        cloud_lat = cloud_ds_var['lat'].values
        cloud_lon = cloud_ds_var['lon'].values
        
        # Create lat/lon grids
        lat_grid, lon_grid = np.meshgrid(cloud_lat, cloud_lon, indexing='ij')
        
        # Fill missing data using interpolation
        cloud_filled = fill_missing_data_with_interpolation(lat_grid, lon_grid, cloud_ds_var.values)

        # # Plot the 2d array using cartopy before and after interpolation
        # fig, ax = plt.subplots(1, 2, figsize=(10, 5), subplot_kw={'projection': ccrs.PlateCarree()})
        # ax[0].pcolormesh(lon_grid, lat_grid, cloud_ds.values, transform=ccrs.PlateCarree(), cmap='Greys')
        # ax[1].pcolormesh(lon_grid, lat_grid, cloud_filled, transform=ccrs.PlateCarree(), cmap='Greys')
        
        # plt.savefig(f"{output_path}{cmsaf_var}interp_{year}{month:02d}{day:02d}_{hour:02d}:{minute:02d}.png")
        
        # Create a new DataArray with the interpolated/regridded data
        regridded_data = xr.DataArray(
            cloud_filled,
            coords={
                "lat": ("lat", cloud_lat),
                "lon": ("lon", cloud_lon),
            },
            dims=("lat", "lon"),
            name=f"{cmsaf_var}_interpolated"
        )
        
        # Find the nearest indices for the given lat and lon
        lat_idx = np.abs(cloud_lat - lat).argmin()
        lon_idx = np.abs(cloud_lon - lon).argmin()
        
        # Retrieve the values at the found indices
        closed_pixel_value = cloud_ds_var.isel(lat=lat_idx, lon=lon_idx).values
        closed_pixel_value_regrid = regridded_data.isel(lat=lat_idx, lon=lon_idx).values
        
        print(f"Value for {cmsaf_var} at closed pixel (lat: {lat}, lon: {lon}): {closed_pixel_value}")
        print(f"Regridded value for {cmsaf_var} (lat: {lat}, lon: {lon}): {closed_pixel_value_regrid}")
        
        # Update the DataFrame with the retrieved values
        df.at[index, f"{cmsaf_var}_value"] = closed_pixel_value
        df.at[index, f"{cmsaf_var}_regridded"] = closed_pixel_value_regrid

    # Save the daily DataFrame to a CSV file
    daily_output_file = f"{output_path}cloud_property_flag/cloud_properties_{date}.csv"
    daily_df.to_csv(daily_output_file, index=False)
    print(f"Saved daily data for {date} to {daily_output_file}")

# Save the filled df

# Save the DataFrame to a CSV file
df.to_csv(f'{output_path}cloud_mask_closed_points_cloud_properties.csv', index=False)

#2403113 nohup