import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap, BoundaryNorm
from glob import glob

modis_cma_path = '/data1/other_data/MODIS/2013/'
modis_filename = 'CLDMSK_L2_MODIS_Aqua*.nc'
output_path = '/home/Daniele/fig/cma_analysis/modis/'

filepattern = modis_cma_path + modis_filename

filelist = sorted(glob(filepattern))
print(f"Found {len(filelist)} files")
for file_path in filelist:
    print(f"Processing file: {file_path}")

    # Open the dataset
    ds = xr.open_dataset(file_path)

    # Extract time attributes
    time_start = ds.attrs.get("time_coverage_start", "Unknown")
    time_end = ds.attrs.get("time_coverage_end", "Unknown")
    print(f"Time coverage: {time_start} - {time_end}")

    # Open the cloud mask and geolocation data
    cloud_mask_ds = xr.open_dataset(file_path, group="geophysical_data")
    geo_ds = xr.open_dataset(file_path, group="geolocation_data")
    #ds_scan_line = xr.open_dataset(file_path, group="scan_line_attributes")

    # Extract data
    cloud_mask = cloud_mask_ds['Integer_Cloud_Mask'].values
    latitude = geo_ds['latitude'].values
    longitude = geo_ds['longitude'].values

    # Mask invalid values
    cloud_mask = np.ma.masked_where(cloud_mask == -1, cloud_mask)  # Handle _FillValue

    # Define a custom colormap and boundaries
    colors = ['blue', 'cyan', 'yellow', 'green']  # Colors for 0, 1, 2, 3
    cmap = ListedColormap(colors)
    bounds = [-0.5, 0.5, 1.5, 2.5, 3.5]  # Boundaries for the integer values
    norm = BoundaryNorm(bounds, cmap.N)

    # Plot with cartopy
    fig, ax = plt.subplots(
        figsize=(10, 8),
        subplot_kw={"projection": ccrs.PlateCarree()}
    )

    # Add features to the map
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='black', facecolor='lightgray')
    ax.set_extent([5, 16, 42, 51.5], crs=ccrs.PlateCarree())  # Define geographical bounds [lon_min, lon_max, lat_min, lat_max]

    # Plot the cloud mask
    cloud = ax.pcolormesh(
        longitude, latitude, cloud_mask,
        cmap=cmap,
        norm=norm,
        shading="auto",
        transform=ccrs.PlateCarree()
    )

    # Add a color bar with custom ticks
    cbar = plt.colorbar(cloud, ax=ax, boundaries=bounds, ticks=[0, 1, 2, 3], orientation='vertical', pad=0.05, fraction=0.03)
    cbar.ax.set_yticklabels(['Cloudy', 'Probably Cloudy', 'Probably Clear', 'Confident Clear'], fontsize=14)
    #cbar.set_label("Cloud Mask Categories", fontsize=12)

    # Add gdridlines
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, linewidth=1, color='gray', alpha=0.5, linestyle='--')

    # add lat lon labels
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 14}
    gl.ylabel_style = {'size': 14}

    # Title
    ax.set_title(
        f"MODIS Aqua - Cloud Mask \n {time_start} - {time_end}",
        fontsize=16, fontweight='bold', pad=15
    )

    fig.savefig(f"{output_path}modis_cloud_mask_{time_start}_{time_end}.png", bbox_inches="tight")
    print(f"Saved figure: {output_path}modis_cloud_mask_{time_start}_{time_end}.png")
