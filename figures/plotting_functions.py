import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.cm as cm
import matplotlib.colors as colors


def plot_map(data, lon, lat, data_min, data_max):
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
    #mesh = ax.contourf(msg_lon_grid, msg_lat_grid, cth_regridded, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
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

    plt.title('Cloud Top Height (CTH) from NWC SAF - '+readable_date_time, fontsize=12, fontweight='bold')
    plt.show()
    #fig.savefig(path_fig+'cth_map_'+date_time_str+'.png', bbox_inches='tight')
    plt.close()