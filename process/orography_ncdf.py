
"""
script to produce ncdf file containing orography for the expats domain at highest resolution. Data are
taken from USGS repository and can be accessed from https://topotools.cr.usgs.gov/gmted_viewer/viewer.htm
https://topotools.cr.usgs.gov/GMTED_viewer/gmted2010_fgdc_metadata.html

"""
import rasterio
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from affine import Affine
from pyproj import Proj, transform
import xarray as xr

from readers.files_dirs import raster_filename_1, raster_filename_2
from figures.domain_info import domain_expats

def main():
    
    # read first dataset 
    ds_1 = raster_to_dataset(raster_filename_1)
    ds_2 = raster_to_dataset(raster_filename_2)

    # redefining coordinate of dataset 2 to be able to concatenate 
    ds_2['y'] = np.arange(9600,9600+len(ds_2.lats.values))

    # concatenate the two domains
    ds_concat = xr.concat([ds_1, ds_2], dim="y")
    
    # select domain expats
    minlon, maxlon, minlat, maxlat = domain_expats
    ds_expats = ds_concat.where((ds_concat.lats > minlat) * (ds_concat.lats < maxlat) * (ds_concat.lons > minlon) * (ds_concat.lons < maxlon), drop=True)

    # store to ncdf
    ds_expats.to_netcdf('/net/ostro/figs_proposal_TEAMX/orography_expats_high_res.nc')

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

if __name__ == "__main__":
    main()
    