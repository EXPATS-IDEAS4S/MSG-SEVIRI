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

# Open the NetCDF file
# Path to your NetCDF file
path_to_files = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/'
path_fig = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/Fig/CTH_maps/'
#nc_file = 'CTXin20210712000000405SVMSGI1UD.nc'

#open all files in directory 
nc_file = "CTX*.nc"

fnames = sorted(glob(path_to_files+nc_file))
print(fnames)

#Read data at different temporal steps
for t,f in enumerate(fnames):
    file = f.split('/')[-1]

    dataset = nc.Dataset(path_to_files+file)

    # Extract the date and time part from the filename
    # Assuming the format is consistent and the date/time part always starts at the 5th character and is 12 characters long
    date_time_str = file[5:17]

    # Convert the string to a datetime object
    date_time_obj = datetime.strptime(date_time_str, '%Y%m%d%H%M')

    # Format the datetime object into a more readable string
    # For example, "July 12, 2021, 00:00"
    readable_date_time = date_time_obj.strftime('%m %d, %Y, %H:%M')
    print(readable_date_time)

    # Extract x and y variables
    x = dataset.variables['x'][:]
    y = dataset.variables['y'][:]
    h = dataset.variables['subsatellite_alt'][:][0]

    #print("x: ", np.shape(x), x)
    #print("y: ", np.shape(y), y)
    #print('h', h)

    # Define the source projection (geostationary) with parameters from your file
    geos_proj = pyproj.Proj(proj='geos', h=h, lon_0=0.0, sweep='y', a=6378169.0, b=6356583.8)

    # Define the target projection as WGS84 (latitude and longitude in degrees)
    wgs84_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    # Create a transformer
    transformer = pyproj.Transformer.from_proj(geos_proj, wgs84_proj, always_xy=True)

    # Step 1: Create a mesh grid
    x_mesh, y_mesh = np.meshgrid(x, y)

    # Convert x and y from radians to meters using the satellite height
    # Note: Perform this operation directly on the mesh grid
    x_meters_mesh = x_mesh * h
    y_meters_mesh = y_mesh * h

    # Step 2: Flatten the mesh grid arrays to 1D arrays for transformation
    x_meters_flat = x_meters_mesh.flatten()
    y_meters_flat = y_meters_mesh.flatten()

    # Step 3: Transform coordinates
    lon_flat, lat_flat = transformer.transform(x_meters_flat, y_meters_flat)

    # Now lon_flat and lat_flat are 1D arrays; you can reshape them back to 2D if needed
    lon = lon_flat.reshape(x_mesh.shape)
    lat = lat_flat.reshape(y_mesh.shape)

    # Print or plot your results as needed
    #print("Transformed Longitude (degrees East):", np.shape(lon), lon)
    #print("Transformed Latitude (degrees North):", np.shape(lat), lat)

    # Extract CTH data
    cth = dataset.variables['cth'][:].squeeze()
    #print('CTH', np.shape(cth), cth)

    #regrid to MSG grid
    

    # Plotting setup
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())  # Adjust this based on your projection

    # Plot CTH data
    # Assuming lat and lon are computed or extracted arrays of the same shape as cth

    # Mask invalid data
    #cth_masked = np.ma.masked_where(cth == dataset.variables['cth']._FillValue, cth[0])

    # Create a Normalize object
    norm = colors.Normalize(vmin=1000, vmax=16000) #TODO adjust with the actual max min over all the images
    cmap = 'cool_r'

    # Create a ScalarMappable with the normalization and colormap
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    # Plot
    mesh = ax.contourf(lon, lat, cth, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)

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
    #plt.show()
    fig.savefig(path_fig+'cth_map_'+date_time_str+'.png', bbox_inches='tight')
    plt.close()
