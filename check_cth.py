import netCDF4 as nc
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import pyproj

# Open the NetCDF file
# Path to your NetCDF file
path_to_files = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/'
nc_file = 'CTXin20210712000000405SVMSGI1UD.nc'
dataset = nc.Dataset(path_to_files+nc_file)

# Extract x and y variables
x = dataset.variables['x'][:]
y = dataset.variables['y'][:]
h = dataset.variables['subsatellite_alt'][:][0]

print("x: ", x)
print("y: ", y)
print('h', h)

# Define the source projection (geostationary) with parameters from your file
geos_proj = pyproj.Proj(proj='geos', h=h, lon_0=0.0, sweep='y', a=6378169.0, b=6356583.8)

# Define the target projection as WGS84 (latitude and longitude in degrees)
wgs84_proj = pyproj.Proj(proj='latlong', datum='WGS84')

# Create a transformer
transformer = pyproj.Transformer.from_proj(geos_proj, wgs84_proj, always_xy=True)

# Convert x and y from radians to meters using the satellite height
x_meters = x * h
y_meters = y * h

# Transform coordinates
lon, lat = transformer.transform(x_meters, y_meters)

# lon and lat are now in degrees East and North respectively
print("Longitude (degrees East):", lon)
print("Latitude (degrees North):", lat)

"""

# Extract CTH data
cth = dataset.variables['cth'][:]

# Plotting setup
fig = plt.figure(figsize=(10, 10))
ax = plt.axes(projection=ccrs.PlateCarree())  # Adjust this based on your projection
ax.coastlines()

# Plot CTH data
# Assuming lat and lon are computed or extracted arrays of the same shape as cth
# This is a placeholder for actual lat/lon computation
lat = np.linspace(-81.26, 81.26, cth.shape[1])  # These are example values
lon = np.linspace(-81.2, 81.2, cth.shape[2])
lon, lat = np.meshgrid(lon, lat)

# Mask invalid data
cth_masked = np.ma.masked_where(cth == dataset.variables['cth']._FillValue, cth[0])

# Plot
c = ax.pcolormesh(lon, lat, cth_masked.squeeze(), transform=ccrs.PlateCarree())

# Add color bar
plt.colorbar(c, ax=ax, orientation='vertical', label='Cloud Top Height (m)')

plt.title('Cloud Top Height (CTH)')
plt.show()
"""
