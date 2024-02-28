"""

code to plot distributions of values of channels over expats domain
"""
    
    
from readers.msg_ncdf import read_ncdf, read_orography, read_lat_lon_file

from readers.files_dirs import path_figs, path_dir_tree, raster_filename, orography_file
from figures.domain_info import domain_expats, domain_dfg
from figures.mpl_style import CMAP, plot_cities_expats, plot_local_dfg
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio


def main():
    
    # read data of the month of july
    yy = '2023'
    mm = '07'
    
    # loop on days
    # reading input files
    data = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/')
    
    # reading dimensions of the data
    n_samples, dim_y, dim_x = np.shape(data.IR_108.values)
    print('number of time samples ', n_samples)
    print('calculating percentile')
              
    # calculate 10th percentile
    data_variable = data['IR_108']
    data_variable = data_variable.chunk({'time': len(data_variable.time)})
    q10 = data_variable.quantile(0.1, "time")
    
    #print(np.shape(IR_108_10perc))    
    print(np.nanmax(q10), np.nanmin(q10))
    
    # plot 10percentile
    print('plot map of percentile')
    lons, lats = read_lat_lon_file()
    
    #map_percentiles(IR_108_10perc, data.lat.values, data.lon.values, domain_expats, path_figs)
    #plot_msg(lons, lats, q10, '10th percentiles 10.8 micron', CMAP, domain_expats, path_figs, 'expats')
    plot_msg(lons, lats, q10, '10th percentiles 10.8 micron', CMAP, domain_dfg, path_figs, 'dfg')

def calc_mid_points_pairs_array(x):
    """
    given x, it produces an array containing mean of each pair of consecutive values of x
    args:
    - x input array
    returns:
    - y array of mean values
    
    """    
    y = (x[1:] + x[:-1]) / 2
    print(len(x), len(y))
    return y


def plot_msg(lons, lats, variable, label, cmap, domain, path_out, key):
    """
    plot map of the variable over the defined domain

    Args:
        lons (array): longitude values
        lats (array): latitudes 
        variable (matrix): variable to plot
        label (string): string for plot filename
        cmap (colormap): color map 
        domain (array): minlon, maxlon, minlat, maxlat
        path_out (string): path where to save the plot
        key (string): string possible "expats" or "dfg"
    
    Dependencies:
    plot_cities_expats, 
    plot_local_dfg
    
    """
    

    
    # Plot the map of MSG channels vs lat/lon
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.spines["top"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)
    ax.set_extent(domain)
    
    
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'fontsize': 14}
    gl.ylabel_style = {'fontsize': 14}
    
    
    
    if key == 'dfg':
        
        
        #plot now contour levels for the variable field
        BT_levels = np.linspace(np.nanmin(variable), 250., 20) # scaled for zoomed region
        # plotting on the back, invisible in the end, the field for getting the colormap
        mesh_transp =  ax.contourf(lons, 
                        lats, 
                        variable,
                        transform=ccrs.PlateCarree(), 
                        levels=BT_levels, 
                        alpha=1.,
                        cmap=cmap)
        
        plt.colorbar(mesh_transp,
                     ax=[ax],
                     label='10.8 $\mu$m 10th quantile Brightness Temperature (K)', 
                     shrink=0.6)
               
        # reading orography data from raster file
        ds_or = read_orography()
        oro_levels = np.linspace(0, 4000, 20)
        oro = ax.contourf(ds_or.lons.values, 
                          ds_or.lats.values, 
                          ds_or.orography.values, 
                          transform=ccrs.PlateCarree(), 
                          levels=oro_levels, 
                          alpha=1.,
                          cmap='Greys')
        
         # Add colorbar with reduced size
        plt.colorbar(oro, 
                     ax=[ax], 
                     label='Orography [m]', 
                     shrink=0.6, 
                     location='left')
        
        mesh = ax.contour(lons, 
                        lats, 
                        variable, 
                        levels=BT_levels,
                        cmap=cmap, 
                        transform=ccrs.PlateCarree(),                         
                        linewidths=3.,) 
        
        # labelling contour lines
        ax.clabel(mesh, 
                  levels=BT_levels,  # label every second level
                  inline=True, 
                  fmt='%1.1f', 
                  fontsize=10)

        

        #cbar.ax.set_xticklabels(['225', '230', '235', '240', '245'])  # horizontal colorbar

    elif key == 'expats':
        
        # plot 10th percentile as filled contours
        mesh = ax.contourf(lons, 
                            lats, 
                            variable, 
                            cmap=cmap, 
                            transform=ccrs.PlateCarree(), 
                            vmin=230, 
                            vmax=270) 
        cbar = plt.colorbar(mesh, label='10.8 $\mu$m 10th quantile Brightness Temperature (K)', shrink=0.6)

    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.RIVERS)
    
     #vmin, vmax=220.,
    plt.tick_params(axis='both',which='major',labelsize=14)

    ax.set_xlabel('Latitude [$^{\circ}$]')
    ax.set_ylabel('Longitude [$^{\circ}$]')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)
    #cbar = plt.colorbar(pc,ax=ax,shrink=0.75)
    #cbar.set_label(label, fontsize=14)
    #cbar.ax.tick_params(labelsize=14)

    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=1.5, color='black')
    #ax.add_feature(cfeature.STATES, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=1.5, color='black')
    
    if key =='expats':
        plot_cities_expats(ax, 'grey', 50)
    elif key == 'dfg':
        plot_local_dfg(ax, 'black', 50)
        
        
    plt.savefig(
        os.path.join(path_out, label+"_"+key+".png"),
        dpi=300,
        bbox_inches="tight",
        transparent=True,
        )

    plt.close()


    
if __name__ == "__main__":
    main()
    