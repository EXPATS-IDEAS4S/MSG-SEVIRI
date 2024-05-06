import xarray as xr
import pandas as pd
import datetime
import numpy as np

def insert_time_attr(ds):
    # Step 1: Extract the time value
    time_value = ds['time'].values[0]

    # Step 2: Convert numpy.datetime64 to a formatted string
    formatted_time = pd.Timestamp(time_value).strftime('%Y-%m-%dT%H:%M:%SZ')

    # Step 3: Set as a global attribute
    ds.attrs['nominal_product_time'] = formatted_time

    # Set 4: Remove the 'time' variable from the dataset
    ds = ds.drop_vars('time')

    return ds


def insert_satellite_id(ds):
    # Step 1: Extract the flag value
    flag_value = ds['platform_flag'].values[0]

    # Step 2: Map flag value to satellite name
    # Extract flag meanings and values from attributes
    flag_values = ds['platform_flag'].flag_values
    flag_meanings = ds['platform_flag'].flag_meanings.split()  # Assuming space-separated names

    # Create a mapping dictionary from flag values to meanings
    flag_map = dict(zip(flag_values, flag_meanings))

    # Convert flag value to actual satellite name using the mapping
    satellite_name = flag_map.get(flag_value, "Unknown Satellite")  # Default if not found

    # Step 3: Set as a global attribute
    ds.attrs['satellite_identifier'] = satellite_name

    return ds


def insert_subsatellite_pos_attr(ds):
    # Step 1: Extract the subsat position from variables
    subsat_lon = ds['subsatellite_lon'].values[0].astype('float32')
    subsat_lat = ds['subsatellite_lat'].values[0].astype('float32')
    subsat_alt = ds['subsatellite_alt'].values[0].astype('float32')

    # Step 2: Set as a global attribute
    ds.attrs['sub-satellite_longitude'] = subsat_lon
    ds.attrs['sub-satellite_latitude'] = subsat_lat
    ds.attrs['sub-satellite_altitude'] = subsat_alt

    return ds


def insert_gdal_projection(ds):
    # Extract the projection information
    proj_info = ds['projection']
    
    # Construct the GDAL projection string
    gdal_proj = (
        "+proj=geos "
        f"+a={proj_info.semi_major_axis:.6f} "
        f"+b={proj_info.semi_minor_axis:.6f} "
        f"+lon_0={proj_info.longitude_of_projection_origin:.6f} "
        f"+h={proj_info.perspective_point_height:.6f} "
        f"+sweep={proj_info.sweep_angle_axis}"
    )
    
    # Set as a global attribute
    ds.attrs['gdal projection'] = gdal_proj
    
    return ds


def _is_georef_offset_present(date):
    # Reference: Product User Manual, section 3.
    # https://doi.org/10.5676/EUM_SAF_CM/CLAAS/V002_01
    return date < datetime.date(2017, 12, 6)

def insert_lat_lon(ds, aux_ds):
    # Retrieve the 'nominal_product_time' from global attributes
    #nominal_time_str = ds.attrs.get('nominal_product_time', None)
    
    # if nominal_time_str:
    #     # Convert string to datetime.date object
    #     nominal_date = datetime.datetime.strptime(nominal_time_str, '%Y-%m-%dT%H:%M:%SZ').date()
    #     # Determine if georef offset correction is needed
    #     offset_correction_needed = _is_georef_offset_present(nominal_date)


        
    # Choose the correct lat and lon based on the offset correction
    #coord_idx = 0 if offset_correction_needed else 1
    coord_idx = ds.georef_offset_corrected.values[0]
    lat_var_name = 'lat'  
    lon_var_name = 'lon'  
    
    if lat_var_name in aux_ds and lon_var_name in aux_ds:
        # Extract the latitude and longitude with explicit dimensions
        lat_data = aux_ds[lat_var_name].values[coord_idx,:,:]
        lon_data = aux_ds[lon_var_name].values[coord_idx,:,:]
        
        # Assuming dimensions 'y' and 'x' need to be specified explicitly
        ds[lat_var_name] = (('ny', 'nx'), lat_data)
        ds[lon_var_name] = (('ny', 'nx'), lon_data)
        #ds = ds.set_coords(['lat', 'lon'])
    else:
        print("Correct latitude and longitude data not found in auxiliary dataset.")
    #else:
    #    print("Nominal product time not found in dataset attributes.")

    # Remove 'x' and 'y' variables from ds if they exist
    if 'x' in ds.variables:
        ds = ds.drop_vars('x')
    if 'y' in ds.variables:
        ds = ds.drop_vars('y')
    
    return ds
