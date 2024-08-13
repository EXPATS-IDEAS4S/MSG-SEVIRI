
import xarray as xr
from random import randrange
import numpy as np
import matplotlib.pyplot as plt
import os



def crops_nc(ds_image, x_pixel, y_pixel, n_sample, filename, out_path):
    """
    Generates multiple random crops from the input dataset, saves them in NetCDF and TIFF formats.

    This function takes an input dataset, generates random crops of specified size, and saves
    the crops as NetCDF files to preserve the original values and coordinates. Additionally,
    it saves the cropped images as TIFF files.

    :param ds_image: xarray.Dataset or xarray.DataArray
        The input dataset containing the image data along with latitude and longitude coordinates.
    :param x_pixel: int
        The width of the crop in pixels.
    :param y_pixel: int
        The height of the crop in pixels.
    :param n_sample: int
        The number of random crops to generate.
    :param filename: str
        The base filename for saving the cropped images.
    :param out_path: str
        The output directory where the cropped images will be saved.
    
    :return: None
    """

    #get array size from dataset ds_image 
    x = len(ds_image.lon.values)
    y = len(ds_image.lat.values)
    #print(x,y)
       
    for i in range(n_sample):

        x1 = randrange(0, x - x_pixel)
        y1 = randrange(0, y - y_pixel)
        #print(x1,y1)

        #find lat lon boundaries of the random crop
        latmin = ds_image.lat.values[y1]
        latmax = ds_image.lat.values[y1+y_pixel-1]
        lonmin = ds_image.lon.values[x1]
        lonmax = ds_image.lon.values[x1+x_pixel-1]
        #print([lonmin, lonmax, latmin, latmax])

        #crop the dataset besed on the random x and y (the upper left point of the crop)
        ds_crop = filter_by_domain(ds_image,[lonmin, lonmax, latmin, latmax])
        #print(ds_crop)

        #check if the crop contains any Nan
        isnan_ds = xr.DataArray.isnull(xr.DataArray.sum(ds_crop,skipna=False))

        if isnan_ds==False:
            #save the crops in nc format to keep actual values and lat/lon coordinates
            ds_crop.to_netcdf(out_path+'nc/'+filename+"_"+str(i)+'.nc')
            
            print(out_path+'nc/'+filename+"_"+str(i), 'saved')


def filter_by_domain(ds, domain):
    """
    Filters the input dataset based on a specified geographical domain.

    This function applies a mask to the input dataset to include only the data
    points within the specified latitude and longitude boundaries. The masked 
    dataset is then returned.

    :param ds: xarray.Dataset or xarray.DataArray
        The input dataset containing the data to be filtered.
    :param domain: list or tuple of float
        A list or tuple specifying the domain boundaries in the format 
        [lonmin, lonmax, latmin, latmax], where:
        - lonmin: Minimum longitude
        - lonmax: Maximum longitude
        - latmin: Minimum latitude
        - latmax: Maximum latitude
    
    :return: xarray.Dataset or xarray.DataArray
        The dataset filtered by the specified geographical domain.
    """
    lonmin, lonmax, latmin, latmax = domain
    #Find the mask
    mask = (ds['lat'] >= latmin) & (ds['lat'] <= latmax) & (ds['lon'] >= lonmin) & (ds['lon'] <= lonmax)
    
    # Apply the mask to the dataset
    ds_masked = ds.where(mask, drop=True)

    return ds_masked

def filter_by_time(ds, time):
    """
    Filters the input dataset based on a specified time.

    This function applies a mask to the input dataset to include only the data
    points that match the specified time. The masked dataset is then returned.

    :param ds: xarray.Dataset or xarray.DataArray
        The input dataset containing the data to be filtered.
    :param time: datetime-like object
        The specific time for which the data should be filtered. This can be a 
        datetime object or any other type compatible with the dataset's time coordinate.
    
    :return: xarray.Dataset or xarray.DataArray
        The dataset filtered by the specified time.
    """
    #Find the mask
    mask = (ds['time'] == time)
    
    # Apply the mask to the dataset
    ds_masked = ds.where(mask, drop=True)

    return ds_masked


def compute_global_min_max(file_paths, variable):
    """
    Compute the global minimum and maximum values across all NetCDF datasets.

    :param file_paths: List of paths to NetCDF files.
    :param variable: The variable to analyze.
    :return: (global_min, global_max) values.
    """
    global_min = float('inf')
    global_max = float('-inf')

    for path in file_paths:
        ds = xr.open_dataset(path)
        data = ds[variable].values
        data_min = np.nanmin(data)
        data_max = np.nanmax(data)
        
        # Update global min and max
        global_min = min(global_min, data_min)
        global_max = max(global_max, data_max)
        
        ds.close()

    return global_min, global_max



def create_fig(image, pixel_size, cmap, vmin=None, vmax=None):
    """
    Creates and returns a matplotlib figure with the given pixel size from an image.

    This function generates a matplotlib figure using the specified image and pixel size. 
    The figure is created with `dpi=1` to ensure the pixel size directly corresponds 
    to the figure size.

    :param image: The image to be plotted, compatible with matplotlib's imshow function.
    :param pixel_size: A tuple representing the pixel size (width, height) to be used as the figure size.
    :param vmin: The minimum data value that corresponds to the colormap's lower limit.
    :param vmax: The maximum data value that corresponds to the colormap's upper limit.
    :return: The created matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=pixel_size, dpi=1)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.imshow(image, cmap=cmap, vmin=vmin, vmax=vmax)
    ax.axis(False)
    plt.close(fig)
    return fig



def convert_crops_to_images(ds_image, x_pixel, y_pixel, filename, format, out_path, cmap, vmin, vmax, norm_type):
    """
    Generates a cropped image from the input dataset and saves it in the specified format.

    This function takes an input dataset and generates a cropped image based on the specified 
    pixel dimensions (x_pixel, y_pixel). The cropped image is saved using the specified format 
    (e.g., TIFF, PNG) and file path. The function uses the provided colormap and value range 
    (vmin, vmax) to enhance the image visualization.

    Parameters:
    -----------
    ds_image : xarray.Dataset or xarray.DataArray
        The input dataset or data array containing the image data, typically including 
        associated latitude and longitude coordinates.
    
    x_pixel : int
        The width of the crop in pixels.
    
    y_pixel : int
        The height of the crop in pixels.
    
    filename : str
        The base filename used to save the cropped image.
    
    format : str
        The format in which the cropped image will be saved (e.g., 'tiff', 'png').
    
    out_path : str
        The directory path where the cropped image will be saved.
    
    cmap : str
        The colormap to use for visualizing the image.
    
    vmin : float
        The minimum value for color scaling in the image visualization.
    
    vmax : float
        The maximum value for color scaling in the image visualization.
    
    Returns:
    --------
    None
        The function does not return any value. It saves the cropped image to the specified file path.
    """
    
    #save the images
    fig = create_fig(ds_image.values.squeeze(),[x_pixel,y_pixel], cmap, vmin, vmax)

    # Define output directory
    out_dir = f'{out_path}{format}_{norm_type}'

    # Check if the directory exists
    if not os.path.exists(out_dir):
        # Create the directory if it doesn't exist
        os.makedirs(out_dir) 

    fig.savefig(f'{out_dir}/{filename}_{norm_type}.{format}', dpi=1)

    print(f'{out_dir}/{filename}_{norm_type}.{format} is saved')