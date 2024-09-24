import xarray as xr
from pyproj import Transformer
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from regrid_functions import regrid_data, generate_regular_grid

path_to_files = "/data/sat/msg/orography/"
nc_file = 'RA-Europe-DEM.nc'

path_out = "/data/sat/msg/orography/DEM_expats_1km-reg-grid.nc"

# Define the bounding box for cropping (lonmin, lonmax, latmin, latmax)
lonmin, lonmax = 5, 16
latmin, latmax = 42, 51.5
grid_size = 0.01

# Load the dataset
ds = xr.open_dataset(path_to_files+nc_file)

# Extract GeoTransform parameters (you may need to adjust parsing depending on the format)
geo_transform = ds.spatial_ref.attrs['GeoTransform'].split()

# Extract the CRS (coordinate reference system)
src_crs_wkt = ds.spatial_ref.attrs['crs_wkt']

# Define the transformer from LAEA (current CRS) to lat/lon (WGS84)
transformer = Transformer.from_crs(src_crs_wkt, "EPSG:4326", always_xy=True)

# Get the grid of x and y coordinates
x = ds['x'].values
y = ds['y'].values

# Meshgrid to create all combinations of x and y
xv, yv = np.meshgrid(x, y)

# Apply transformation (from projected coordinates to lat/lon)
lon, lat = transformer.transform(xv, yv)

# Now assign lat/lon as new coordinates in the dataset
ds = ds.assign_coords(lon=(('y', 'x'), lon), lat=(('y', 'x'), lat))

print(ds)

# Create a mask for selecting the desired lat/lon range
lat_mask = (ds['lat'] >= latmin-1) & (ds['lat'] <= latmax+1)
lon_mask = (ds['lon'] >= lonmin-1) & (ds['lon'] <= lonmax+1)

# Combine both masks (only keep points within both lat and lon bounds)
combined_mask = lat_mask & lon_mask

# Find the indexes where the combined mask is True
# This will give us the positions of lat/lon that are inside the desired box
valid_points = combined_mask.where(combined_mask, drop=True)

# Apply this valid point mask to actually select the data
# Select only the non-NaN data, effectively discarding points outside the mask
ds = ds.sel(
    y=valid_points['y'].dropna(dim='y', how='all').coords['y'],
    x=valid_points['x'].dropna(dim='x', how='all').coords['x']
)

print(ds.DEM.values)


# Create a regular grid with 0.01-degree resolution in lat/lon
lat_new, lon_new = generate_regular_grid(latmin,latmax,lonmin,lonmax,grid_size)

lat_reg_grid, lon_reg_grid = np.meshgrid(lat_new, lon_new, indexing='ij')
print(lat_reg_grid)
print(lon_reg_grid)
print(ds.lat.values)
print(ds.lon.values) 
print(ds.DEM.values)

# Interpolate to a regular grid 
regrid_DEM_data = regrid_data(ds.lat.values, ds.lon.values, ds.DEM.values, lat_reg_grid, lon_reg_grid, 'linear')

print(regrid_data)

# Create a new xarray dataset with 1D lat/lon coordinates
cropped_ds = xr.Dataset(
    {
        'DEM': (['lat', 'lon'], regrid_DEM_data)
    },
    coords={
        'lat': lat_new,
        'lon': lon_new
    }
)

print(cropped_ds)




def plot_dem(cropped_ds, title="DEM Data", cmap="terrain"):
    """
    Plots the DEM data from the cropped and regridded dataset.
    
    Parameters:
    cropped_ds (xarray.Dataset): The dataset containing 'lat', 'lon', and 'DEM' variables.
    title (str): Title of the plot.
    cmap (str): Colormap to use for plotting.
    """
    # Extract lat, lon, and DEM values from the dataset
    lat = cropped_ds['lat'].values
    lon = cropped_ds['lon'].values
    dem = cropped_ds['DEM'].values
    
    # Create the plot using Cartopy for better geographical projection
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Plot the DEM data as a color mesh
    dem_plot = ax.pcolormesh(lon, lat, dem, cmap=cmap, shading='auto', transform=ccrs.PlateCarree())

    # Add coastlines and borders for reference
    ax.coastlines(resolution='10m', color='black')
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    
    # Add colorbar
    cbar = plt.colorbar(dem_plot, ax=ax, orientation='vertical', pad=0.05, aspect=50)
    cbar.set_label('Elevation (m)')
    
    # Set the title
    ax.set_title(title, fontsize=14)
    
    # Save the plot
    fig.savefig(path_out.split('.')[0]+'.png', bbox_inches='tight')


# Call the plotting function after regridding the dataset
#plot_dem(cropped_ds, title="Cropped and Regridded DEM")


# Optionally, you can save the transformed dataset to a new file
cropped_ds.to_netcdf(path_out)

print("Transformation and interpolation complete. The dataset is now in a regular lat/lon grid.")
