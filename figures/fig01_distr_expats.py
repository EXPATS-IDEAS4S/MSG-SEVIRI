"""

code to plot distributions of values of channels over expats domain
"""
    
    
from readers.msg_ncdf import read_ncdf

from readers.files_dirs import path_figs, raster_filename
from figures.domain_info import domain_dfg
from figures.mpl_style import CMAP
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt


def main():
    
    
    # reading input files
    data = read_ncdf()
    print(data)
    
    IR_108_10perc = np.zeros((len(data.lon_grid.values), len(data.lat_grid.values)))
    IR_108_10perc.fill(np.nan)
    
    # calculate 10th percentile of 10.8 IR BT  
    for i_x in range(len(data.lat_grid.values)):
        for i_y in range(len(data.lon_grid.values)):
                IR_108_10perc[i_y, i_x] = np.percentile(data.IR_108.values[:, i_y, i_x], 10)
                
    print(IR_108_10perc)    
    
    # plot 10percentile
    map_percentiles(IR_108_10perc, data.lat_grid.values, data.lon_grid.values, domain_dfg, raster_filename, path_figs)
        

def map_percentiles(data, lat, lon, domain, raster_filename, path_figs, plot_city='True'):
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
    

    # Extract main domain boundaries
    minlat_main, maxlat_main, minlon_main, maxlon_main = domain

    with rasterio.open(raster_filename) as src:
        
        data_crs = ccrs.PlateCarree()
        fig = plt.figure(figsize=(10, 8))
        ax = plt.axes(projection=ccrs.PlateCarree())

        ax.contourf(lat, lon, data, transform=data_crs)

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


       
        # add title
        ax.set_title(title+' - '+time_period,fontsize=14,fontweight='bold')


        # Adjust layout and show the plot
        plt.tight_layout()
        plt.show()
        
        
        fig.savefig(path_figs+title+'.png',bbox_inches='tight')
    
if __name__ == "__main__":
    main()
    