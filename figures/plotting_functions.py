import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import matplotlib.cm as cm
import matplotlib.colors as colors


def plot_single_map(data, lon, lat, cmap, norm, extent, date_time_str, data_name_str, label, path_fig=None):
    # Plotting setup
    fig = plt.figure(figsize=(10, 10))
    ax = plt.axes(projection=ccrs.PlateCarree())  # Adjust this based on your projection

    set_map_plot(ax,norm,cmap,extent,data_name_str,label)

    # Plot
    #mesh = ax.contourf(msg_lon_grid, msg_lat_grid, cth_regridded, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
    mesh = ax.contourf(lon, lat, data, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)

    plt.title(data_name_str+' - '+str(date_time_str), fontsize=12, fontweight='bold')

    #ax.plot(8.487149, 48.056274, 'ro', transform=ccrs.PlateCarree())

    #import matplotlib.patches as patches

    # Create a rectangle with the given coordinates
    #rect = patches.Rectangle((8.42, 48.0), 0.12, 0.10, linewidth=2, edgecolor='red', facecolor='none', transform=ccrs.PlateCarree())

    # Add the rectangle to the map
    #ax.add_patch(rect)

    # Plot the cross at the coordinates
    #ax.plot(8.403889, 49.009167, 'rx', markersize=12, transform=ccrs.PlateCarree())  # 'rx' for red cross

    # Add the text label "Karlsruhe" near the cross
    #ax.text(8.403889, 49.009167, 'Karlsruhe', transform=ccrs.PlateCarree(), fontsize=12, color='yellow', ha='left')

    
    if path_fig:
        fig.savefig(path_fig+data_name_str.replace(' ','_')+'_'+str(date_time_str).replace(' ','_')+'.png', bbox_inches='tight')
    else:
        plt.show()
    plt.close()


def set_map_plot(ax, norm, cmap, extent, plot_title, label):
    # Create a ScalarMappable with the normalization and colormap
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    # Add color bar
    plt.colorbar(sm, ax=ax, orientation='vertical', label=label, shrink=0.7)

    #set axis thick labels
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                    linewidth=0.75, color='gray', alpha=0.6, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    gl.xlines = True
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'size': 10, 'color': 'black'}
    gl.ylabel_style = {'size': 10, 'color': 'black'}

    # Adds coastlines and borders to the current axes
    ax.coastlines(resolution='50m', linewidths=0.5, color='yellow') 
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='yellow')
    ax.set_extent(extent) #[left, right, bottom ,top]
    ax.add_feature(cfeature.OCEAN, facecolor='blue')
    #ax.add_feature(cfeature.LAKES, alpha=0.5)
    #ax.add_feature(cfeature.RIVERS)

    ax.set_title(plot_title, fontsize=12, fontweight='bold')
    

def calc_channels_max_min(channels,ds):
    chs_max = []
    chs_min = []
    for ch in channels:
        chs_min.append(ds[ch].values.min())
        chs_max.append(ds[ch].values.max())

    return chs_min, chs_max

