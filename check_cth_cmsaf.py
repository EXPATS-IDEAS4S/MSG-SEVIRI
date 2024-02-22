import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import pyproj
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from datetime import datetime
from glob import glob
import matplotlib.cm as cm
import matplotlib.colors as colors
from scipy.interpolate import griddata
import xarray as xr
import os

### Define Paths ###

#path where cth data are stored
path_to_files = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/CM_SAF/'

#path to save the images
path_fig = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/Fig/CTH_maps/'

#path to retrieve MSG coordinates
msg_file = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_Flood_domain_DataTailor_nat/HRSEVIRI_20210712_20210715_Processed/MSG4-SEVI-MSG15-0100-NA-20210714121243.nc'

#open all files in directory 
nc_file = "CTX*.nc" #'CTXin20210712000000405SVMSGI1UD.nc'
fnames = sorted(glob(path_to_files+nc_file))
#print(fnames)

#open all files using xarray
ds_cth = xr.open_mfdataset(fnames, combine='nested', concat_dim='time', parallel=True)
print(ds_cth)#['ctth_alti'][:].values)


variable_name = 'cth'
print(np.sum((~np.isnan(ds_cth[variable_name][:].values))))

cth_min = np.amin(ds_cth[variable_name][:]).values
cth_max = np.amax(ds_cth[variable_name][:]).values
print('cth min-max: ', cth_min,cth_max)

### Get lan lon from MSG ###

#open NC file
with nc.Dataset(msg_file, 'r') as msg_data:
    msg_lat = msg_data['lat grid'][:] 
    msg_lon = msg_data['lon grid'][:] 

#adjust the shape of the grid (position (0,0) corresponds to the northeastern point)
msg_lon_grid, msg_lat_grid = np.flip(msg_lon[0,:,:]), np.flip(msg_lat[0,:,:]) 
print(np.shape(msg_lat_grid), msg_lat_grid) # first row is the north
print(np.shape(msg_lon_grid), msg_lon_grid) # forst column is the east

#Read, Regrid, Plot data at different temporal steps
for t,f in enumerate(fnames):
    ### Open Netcdf data and read variables ###

    # Extract the date and time part from the filename
    # Assuming the format is consistent and the date/time part always starts at the 5th character and is 12 characters long
    file = f.split('/')[-1]
    date_time_str = file[5:17]

    # Convert the string to a datetime object
    date_time_obj = datetime.strptime(date_time_str, '%Y%m%d%H%M')

    # Format the datetime object into a more readable string. For example, "July 12, 2021, 00:00"
    readable_date_time = date_time_obj.strftime('%m %d, %Y, %H:%M')
    print(readable_date_time)

    # Extract variables
    with nc.Dataset(path_to_files+file) as dataset:
        #print(dataset.variables)
        time = dataset.variables['time'][:]
        x = dataset.variables['x'][:] #zonal angles satellite and point of measurement (rad)
        y = dataset.variables['y'][:] #meridional angle ''
        h = dataset.variables['subsatellite_alt'][:][0] #satellite hight
        cth = dataset.variables[variable_name][:].squeeze() #Cloud top height
    #print('CTH', np.shape(cth), cth)
    #print("x: ", np.shape(x), x)
    #print("y: ", np.shape(y), y)
    #print('h', h)

    ### Project coordinates in a lat/lon grid ###

    # Define the source projection (geostationary) with parameters from your file. TODO Get parameters from metadata
    geos_proj = pyproj.Proj(proj='geos', h=h, lon_0=0.0, sweep='y', a=6378169.0, b=6356583.8)

    # Define the target projection as WGS84 (latitude and longitude in degrees)
    wgs84_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    # Create a transformer
    transformer = pyproj.Transformer.from_proj(geos_proj, wgs84_proj, always_xy=True)

    # Create a mesh grid
    x_mesh, y_mesh = np.meshgrid(x, y)

    # Convert x and y from radians to meters using the satellite height
    # Note: Perform this operation directly on the mesh grid
    x_meters_mesh = x_mesh * h
    y_meters_mesh = y_mesh * h

    # Flatten the mesh grid arrays to 1D arrays for transformation
    x_meters_flat = x_meters_mesh.flatten()
    y_meters_flat = y_meters_mesh.flatten()

    # Transform coordinates to lat/lon
    lon_flat, lat_flat = transformer.transform(x_meters_flat, y_meters_flat)

    # Now lon_flat and lat_flat are 1D arrays; you can reshape them back to 2D if needed
    #lon = lon_flat.reshape(x_mesh.shape)
    #lat = lat_flat.reshape(y_mesh.shape)

    # Print or plot your results as needed
    #print("Transformed Longitude (degrees East):", np.shape(lon), lon)
    #print("Transformed Latitude (degrees North):", np.shape(lat), lat)
    

    ### Regrid to MSG grid ###
        
    # create a 1D array for cth values and lat-lon grids 
    cth_flat = cth.flatten()
    #lon_flat = lon.flatten()
    #lat_flat = lat.flatten()
    
    # Create a 2D mesh grid for the MSG data
    msg_points = np.array([msg_lat_grid.flatten(), msg_lon_grid.flatten()]).T

    # Mask NaN values
    valid = ~np.isnan(cth_flat)
    cth_valid = cth_flat[valid]
    lon_valid = lon_flat[valid]
    lat_valid = lat_flat[valid]

    # create a 2D mesh grid for the lat-lon location
    cth_points = np.array([lat_valid, lon_valid]).T

    # Perform the regridding
    cth_regridded_flat = griddata(cth_points, cth_valid, msg_points, method='nearest')

    # Reshape the regridded data back to 2D (if necessary)
    cth_regridded = cth_regridded_flat.reshape(msg_lat_grid.shape)

    # Set values below the cth_min to NaN to mask really low values that come up after the regridding procedure
    cth_regridded[cth_regridded < cth_min] = np.nan

    #print('regrid cth',np.shape(cth_regridded),cth_regridded)

    ### Save the regridded data to Netcdf ###

    # Define a new filename for saving regridded data
    save_filename = os.path.join(path_to_files+'CTH_regrid', 'regridded_' + os.path.basename(f))

    with nc.Dataset(save_filename, 'w', format='NETCDF4') as nc_save:
        # Assuming msg_lat, msg_lon, and regridded_data are 2D arrays of shape (x_dim, y_dim)
        x_dim, y_dim = msg_lat_grid.shape

        # Create dimensions
        nc_save.createDimension('x', x_dim)
        nc_save.createDimension('y', y_dim)
        nc_save.createDimension('time', 1)

        # Create variables
        times_nc = nc_save.createVariable('time', 'f4', ('time',))
        latitudes_nc = nc_save.createVariable('lat', 'f4', ('x', 'y',))
        longitudes_nc = nc_save.createVariable('lon', 'f4', ('x', 'y',))
        rain_rate_nc = nc_save.createVariable('cth', 'f4', ('x', 'y',), fill_value=np.nan)

        # Assign data to variables
        times_nc[:] = time
        latitudes_nc[:, :] = msg_lat_grid
        longitudes_nc[:, :] = msg_lon_grid
        rain_rate_nc[:, :] = cth_regridded

    print(f"Regridded data saved as {save_filename}")

    ### Plot CTH data ###
    
    # Plotting setup
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())  # Adjust this based on your projection

    # Create a Normalize object
    norm = colors.Normalize(vmin=cth_min, vmax=cth_max) #TODO adjust with the actual max min over all the images
    cmap = 'cool_r'

    # Create a ScalarMappable with the normalization and colormap
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    # Plot
    mesh = ax.contourf(msg_lon_grid, msg_lat_grid, cth_regridded, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)

    # Add color bar
    plt.colorbar(sm, ax=ax, orientation='vertical', label='CTH (m)', shrink=0.8)

    #set axis thick labels
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=0, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlines = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10, 'color': 'black'}
    gl.ylabel_style = {'size': 10, 'color': 'black'}

    # Adds coastlines and borders to the current axes
    ax.coastlines(resolution='50m', linewidths=0.5) 
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='black')
    ax.set_extent([5, 9, 48, 52]) #left, right, bottom ,top

    plt.title('Cloud Top Height (CTH) from CM SAF - '+readable_date_time, fontsize=12, fontweight='bold')
    plt.show()
    #fig.savefig(path_fig+'cth_map_'+date_time_str+'.png', bbox_inches='tight')
    plt.close()
