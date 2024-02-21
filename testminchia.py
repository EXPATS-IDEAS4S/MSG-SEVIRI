
#%%
import rasterio
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from pyproj import Proj, transform
import xarray as xr

domain_expats       =  [ 5.,   16.,    42.,   51.5 ] # minlon, maxlon, minlat, maxlat
lonmin, lonmax, latmin, latmax = domain_expats

# file path for raster 
raster_filename = '/net/ostro/30N000E_20101117_gmted_dsc150.tif'

# Read raster
with rasterio.open(raster_filename) as r:
    T0 = r.transform  # upper-left pixel corner affine transform
    p1 = Proj(r.crs)
    A = r.read()  # pixel values

# All rows and columns
cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

# Get affine transform for pixel centres
T1 = T0 * Affine.translation(0.5, 0.5)
# Function to convert pixel row/column index (from 0) to easting/northing at centre
rc2en = lambda r, c: (c, r) * T1

# All eastings and northings (there is probably a faster way to do this)
eastings, northings = np.vectorize(rc2en, otypes=[float, float])(rows, cols)

# Project all longitudes, latitudes
p2 = Proj(proj='latlong',datum='WGS84')
longs, lats = transform(p1, p2, eastings, northings)

print(np.shape(longs), np.shape(lats), np.shape(A))
y, x = np.shape(longs)


# store data in xarray dataset
ds_out = xr.Dataset(
    data_vars = {'orography':(('y', 'x'), A[0, :, :]), 
                 'lons':(('y', 'x'), lats),
                 'lats':(('y', 'x'), longs),
                 }, 
    coords = {'y':(('y'), np.arange(y)), 
              'x':(('x'), np.arange(x)), 
              }
)

# crop ds dataset to expats domain
lats = ds_out.lats.values
lons = ds_out.lons.values

# selecting expats domain
#i_expats = np.where((lats > latmin) * (lats < latmax) * (lon > lonmin) * (lon > lonmax))[0]

ds_expats = ds_out.where((ds_out.lats > latmin) * (ds_out.lats < latmax) * (ds_out.lons > lonmin) * (ds_out.lons < lonmax), drop=True)


print(ds_expats)
ds_expats.to_netcdf('/net/ostro/figs_proposal_TEAMX/orography_expats.nc')

#%%

plt.contourf(ds_out.lons.values, 
             ds_out.lats.values, 
             ds_out.orography.values, 
             cmap='Spectral')
plt.show()
# %%
#                        transform=ccrs.PlateCarree()) 




#%%
# file path for raster 
raster_filename_1 = '/net/ostro/50N000E_20101117_gmted_max075.tif'
raster_filename_2 = '/net/ostro/30N000E_20101117_gmted_max075.tif'


def raster_to_dataset(raster_file):
    """
    function to convert raster object in xarray dataset

    Args:
        raster_file (string): filename including path of the raster file
    Returns:
        ds_out : xarray dataset containing input data
    """
    # Read raster
    with rasterio.open(raster_file) as r:
        T0 = r.transform  # upper-left pixel corner affine transform
        p1 = Proj(r.crs)
        A = r.read()  # pixel values

    # All rows and columns
    cols, rows = np.meshgrid(np.arange(A.shape[2]), np.arange(A.shape[1]))

    # Get affine transform for pixel centres
    T1 = T0 * Affine.translation(0.5, 0.5)
    # Function to convert pixel row/column index (from 0) to easting/northing at centre
    rc2en = lambda r, c: (c, r) * T1

    # All eastings and northings (there is probably a faster way to do this)
    eastings, northings = np.vectorize(rc2en, otypes=[float, float])(rows, cols)

    # Project all longitudes, latitudes
    p2 = Proj(proj='latlong',datum='WGS84')
    longs, lats = transform(p1, p2, eastings, northings)
    y, x = np.shape(longs)

    
    # store data in xarray dataset
    #ds_out = xr.Dataset(
    #     {'orography':(('y', 'x'), A[0, :, :]), 
    #                'lons':(('y', 'x'), lats),
    #                'lats':(('y', 'x'), longs),
    #                })
    
    
    
    # store data in xarray dataset
    ds_out = xr.Dataset(
        data_vars = {'orography':(('y', 'x'), A[0, :, :]), 
                    'lons':(('y', 'x'), lats),
                    'lats':(('y', 'x'), longs),
                    }, 
        coords = {'y':(('y'), np.arange(y)), 
                'x':(('x'), np.arange(x)), 
                }
    )
    return ds_out

# read first dataset 
ds_1 = raster_to_dataset(raster_filename_1)
ds_2 = raster_to_dataset(raster_filename_2)

#%%
# redefining coordinate of dataset 2 to be able to concatenate 
ds_2['y'] = np.arange(9600,9600+len(ds_2.lats.values))

ds_concat = xr.concat([ds_1, ds_2], dim="y")

# %%

plt.contourf(ds_concat.lons.values, 
             ds_concat.lats.values, 
             ds_concat.orography.values, 
             cmap='Spectral')
plt.show()
# %%
