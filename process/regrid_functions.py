"""
This module provides functions for regridding operations. 
It includes utilities for generating a regular grid based 
on specified geographic boundaries and resolution, 
regridding data from an old grid to a new grid, 
and filling missing data within a dataset using interpolation.

@author: Daniele Corradini
"""

import numpy as np
from scipy.interpolate import griddata

def generate_regular_grid(lat_min, lat_max, lon_min, lon_max, step_deg, path=None):
    """
    Generate a regular grid for a given bounding box and step size in degrees.

    :param lat_min: Minimum latitude of the bounding box.
    :param lat_max: Maximum latitude of the bounding box.
    :param lon_min: Minimum longitude of the bounding box.
    :param lon_max: Maximum longitude of the bounding box.
    :param step_deg: The step size in degrees for both latitude and longitude.
    :param path: If given save the lat and lon regular points there
    :return: A 1D array of regular lat and lon points.
    """
    lat_points = np.arange(lat_min, lat_max + step_deg, step_deg)
    lon_points = np.arange(lon_min, lon_max + step_deg, step_deg)

    if path:
        np.save(path+'reg_lats.npy', lat_points)
        np.save(path+'reg_lons.npy', lon_points)

    return lat_points, lon_points


def regrid_data(old_lat, old_lon, old_data, new_lat, new_lon, method='linear'):
    """
    Regrid data from an old grid to a new grid. If the old data contains only NaN values,
    returns a NaN-filled array matching the shape of the new grid.

    :param old_lat: 2D array of latitudes for the old grid.
    :param old_lon: 2D array of longitudes for the old grid.
    :param old_data: 2D array of data corresponding to the old grid.
    :param new_lat: 2D array of latitudes for the new grid.
    :param new_lon: 2D array of longitudes for the new grid.
    :param method: Interpolation method ('linear', 'nearest', 'cubic').
    :return: 2D array of regridded data corresponding to the new grid.
    """
    # Check if all data points in the old_data are NaN
    if np.all(np.isnan(old_data)):
        # Return a NaN-filled array with the same shape as the new grid
        return np.full(new_lat.shape, np.nan)

    # Flatten the old grid coordinates and data for interpolation
    old_coords = np.array([old_lat.ravel(), old_lon.ravel()]).T
    old_data_flat = old_data.ravel()

    # Create a mesh of new grid coordinates
    new_coords = np.array([new_lat.ravel(), new_lon.ravel()]).T

    # Interpolate old data to new grid using the specified method
    new_data_flat = griddata(old_coords, old_data_flat, new_coords, method=method)

    # Reshape the flattened data back into the 2D structure of the new grid
    new_data = new_data_flat.reshape(new_lat.shape)

    return new_data


def fill_missing_data_with_interpolation(lat, lon, data, method='linear'):
    """
    Fill missing data (NaN) with interpolation based on nearby values. If all data are NaN,
    returns an array of the same shape filled with NaN.

    :param lat: 2D array of latitudes.
    :param lon: 2D array of longitudes.
    :param data: 2D array of data with NaN values for missing data.
    :param method: Interpolation method ('linear', 'nearest', 'cubic').
    :return: 2D array with missing data filled or all NaN if no valid data points exist.
    """
    # Mask to identify valid (non-NaN) data points
    valid_mask = ~np.isnan(data)
    # Check if there are any valid data points
    if not valid_mask.any():
        # Return an array of NaNs with the same shape as the input data if no valid data points
        return np.full(data.shape, np.nan)

    # Coordinates and data of valid points
    valid_data = data[valid_mask]
    valid_lat = lat[valid_mask]
    valid_lon = lon[valid_mask]

    # Linear interpolation for missing data
    filled_data = griddata((valid_lat, valid_lon), valid_data, (lat, lon), method=method)

    return filled_data




"""
# Example usage
from config_satpy_process import lonmin, latmin, lonmax, latmax
step_deg = 0.03  # Define the step size in degrees

lat_grid, lon_grid = generate_regular_grid(latmin, latmax, lonmin, lonmax, step_deg)
print("Regular grid points (lat, lon):")
print(lat_grid, '\n', lon_grid)

"""