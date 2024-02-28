"""

code to plot distributions of values of channels over expats domain
"""
    
    
from readers.msg_ncdf import read_ncdf, read_orography

from readers.files_dirs import path_figs, path_dir_tree, raster_filename, orography_file
from figures.domain_info import domain_expats, domain_dfg
from figures.mpl_style import CMAP
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
    data = read_ncdf()
    print(data)
    
    # reading dimensions of the data
    n_samples, dim_y, dim_x = np.shape(data.IR_108.values)
    print('number of time samples ', n_samples)
    print('calculating percentile')
              
    # calculate 10th percentile
    data_variable = data['IR_108']
    data_variable = data_variable.chunk({'end_time': len(data_variable.end_time)})
    q10 = data_variable.quantile(0.1, "end_time")
    
    #print(np.shape(IR_108_10perc))    
    ##print(np.nanmax(IR_108_10perc), np.nanmin(IR_108_10perc))
    
    # plot 10percentile
    print('plot map of percentile')
    #map_percentiles(IR_108_10perc, data.lat.values, data.lon.values, domain_expats, path_figs)
    plot_msg(data.lat.values, data.lon.values, q10, '10th percentiles 10.8 micron', CMAP, domain_dfg, path_figs)
    
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


def plot_msg(lons, lats, variable, label, cmap, domain, path_out):
    
    # reading orography data from raster file
    ds_or = read_orography()
    
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
    
    mesh = ax.contourf(lons, 
                        lats, 
                        variable, 
                        cmap=cmap, 
                        transform=ccrs.PlateCarree()) 
 
    oro = ax.contourf(ds_or.lons.values, 
                      ds_or.lats.values, 
                      ds_or.orography.values, 
                      cmap='Greys', 
                      alpha = 0.4)
    
    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.RIVERS)
    
    
    # Add colorbar with reduced size
    cbar = plt.colorbar(mesh, label='Brightness Temperature (K)', shrink=0.6)
    #vmin, vmax=220.,
    plt.tick_params(axis='both',which='major',labelsize=14)

    ax.set_xlabel('Latitude [$^{\circ}$]')
    ax.set_ylabel('Longitude [$^{\circ}$]')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)
    #cbar = plt.colorbar(pc,ax=ax,shrink=0.75)
    cbar.set_label(label, fontsize=14)
    cbar.ax.tick_params(labelsize=14)

    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5, color='black')
    ax.add_feature(cfeature.STATES, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=1., color='black')
        
    #add majot city coordinates
    trento = [46.0667, 11.1167] #lat, lon
    bolzano = [46.4981, 11.3548]
    Penegal = [46.43921, 11.2155]
    Tarmeno = [46.34054, 11.2545]
    Vilpiano = [46.55285, 11.20195]
    Sarntal = [46.56611, 11.51642]
    Cles_Malgolo = [46.38098, 11.08136]
    
    # Plot the points
    ax.scatter(trento[1], trento[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())
    ax.scatter(bolzano[1], bolzano[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())
    ax.scatter(Penegal[1], Penegal[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())
    ax.scatter(Cles_Malgolo[1], Cles_Malgolo[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())                        
    ax.scatter(Tarmeno[1], Tarmeno[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())            
    ax.scatter(Vilpiano[1], Vilpiano[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())            
    ax.scatter(Sarntal[1], Sarntal[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())            

    # Plot the names next to the points, adjusted for lower right positioning
    ax.text(trento[1] + 0.02, trento[0] - 0.02, 'Trento', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(bolzano[1] + 0.02, bolzano[0] - 0.02, 'Bolzano', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Penegal[1] + 0.02, Penegal[0] - 0.02, 'Penegal', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Cles_Malgolo[1] + 0.02, Cles_Malgolo[0] - 0.02, 'Cles_Malgolo', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Tarmeno[1] + 0.02, Tarmeno[0] - 0.02, 'Tarmeno', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Vilpiano[1] + 0.02, Vilpiano[0] - 0.02, 'Vilpiano', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
    ax.text(Sarntal[1] + 0.02, Sarntal[0] - 0.02, 'Sarntal', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')

    plt.show()
    
    plt.savefig(
        os.path.join(path_out, label+"_dfg.png"),
        dpi=300,
        bbox_inches="tight",
        transparent=True,
        )

    plt.close()


def map_percentiles(data, lat, lon, domain, path_figs, plot_city='True'):
    """
    Plot geographic event data on a map.

    This function visualizes the geographical distribution of events within specified domains on a map. 
    The map is overlaid with raster data for contextual geographical information. Events are categorized by type 
    and colored by the month of occurrence. Optionally, major city locations can be plotted on the map. 
    The function saves the generated plot as a PNG file.

    Parameters:
    - data (xarray dataset): dataset containing hail/rain events
    - domain (tuple): A tuple containing the latitude and longitude boundaries of the main domain in the form (minlat, maxlat, minlon, maxlon).
    - raster_filename (str): Filename of the raster file to be used as a background map.
    - title (str): The title for the map plot.
    - path_file (str): Path to the directory containing the raster file.
    - path_figs (str): Path to the directory where the plot image will be saved.
    - plot_city (bool): A flag to indicate whether to plot major city locations (True) or not (False).
    """
    # define title and domain
    time_period = '2000-2024'
    title = '10th percentiles 10.8 BT distributions'
    minlon, maxlon, minlat, maxlat = domain
    extent_param = [minlon, maxlon, minlat, maxlat]
        
    # Plot the map of MSG channels vs lat/lon
    crs = ccrs.PlateCarree()

    fig = plt.figure(figsize=(14,14))
    ax = fig.add_subplot(1, 1, 1, projection=crs)
    ax.spines["top"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)

    ax.set_extent(extent_param)

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'fontsize': 14}
    gl.ylabel_style = {'fontsize': 14}
    
    pc = ax.pcolormesh(lon,
                       lat,
                       data.T, 
                       shading='nearest',
                       cmap='Blues')
    
    #vmin, vmax=220.,
    plt.tick_params(axis='both',which='major',labelsize=14)

    ax.set_xlabel('Latitude [$^{\circ}$]')
    ax.set_ylabel('Longitude [$^{\circ}$]')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)
    cbar = plt.colorbar(pc,ax=ax,shrink=0.75)
    cbar.set_label('10th perc Brightness temperature [C]',\
                fontsize=14)
    cbar.ax.tick_params(labelsize=14)

    if plot_city:
        #add majot city coordinates
        trento = [46.0667, 11.1167] #lat, lon
        bolzano = [46.4981, 11.3548]
        Penegal = [46.43921, 11.2155]
        Tarmeno = [46.34054, 11.2545]
        Vilpiano = [46.55285, 11.20195]
        Sarntal = [46.56611, 11.51642]
        Cles_Malgolo = [46.38098, 11.08136]
        
        # Plot the points
        ax.scatter(trento[1], trento[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())
        ax.scatter(bolzano[1], bolzano[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())
        ax.scatter(Penegal[1], Penegal[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())
        ax.scatter(Cles_Malgolo[1], Cles_Malgolo[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())                        
        ax.scatter(Tarmeno[1], Tarmeno[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())            
        ax.scatter(Vilpiano[1], Vilpiano[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())            
        ax.scatter(Sarntal[1], Sarntal[0], marker='x', color='black', s=50, transform=ccrs.PlateCarree())            

        # Plot the names next to the points, adjusted for lower right positioning
        ax.text(trento[1] + 0.02, trento[0] - 0.02, 'Trento', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
        ax.text(bolzano[1] + 0.02, bolzano[0] - 0.02, 'Bolzano', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
        ax.text(Penegal[1] + 0.02, Penegal[0] - 0.02, 'Penegal', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
        ax.text(Cles_Malgolo[1] + 0.02, Cles_Malgolo[0] - 0.02, 'Cles_Malgolo', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
        ax.text(Tarmeno[1] + 0.02, Tarmeno[0] - 0.02, 'Tarmeno', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
        ax.text(Vilpiano[1] + 0.02, Vilpiano[0] - 0.02, 'Vilpiano', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')
        ax.text(Sarntal[1] + 0.02, Sarntal[0] - 0.02, 'Sarntal', color='black', transform=ccrs.PlateCarree(), ha='left', va='top')


       



    # Adjust layout and show the plot
    plt.tight_layout()
    plt.show()
        
        
    fig.savefig(path_figs+title+'.png',bbox_inches='tight')
    
if __name__ == "__main__":
    main()
    