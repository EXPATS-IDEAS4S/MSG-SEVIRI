"""

code to plot distributions of values of channels over expats domain
"""
    
from readers.cm_saf import read_CM_SAF, read_lat_lon_CMSAF
from readers.msg_ncdf import read_ncdf, read_orography, read_lat_lon_file
from readers.files_dirs import path_figs, path_dir_tree, raster_filename, orography_file, CM_SAF_path
from figures.domain_info import domain_expats, domain_dfg
from figures.mpl_style import CMAP, CMAP_an, plot_cities_expats, plot_local_dfg
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.patches as mpatches
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import os
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import shutil
import glob
import itertools
def main():
    
    # read data of the month of july
    yy_arr = ['2023'] # processed years 2022
    mm_arr = ['04', '05', '06', '07', '08', '09']
    
    for yy in yy_arr:
        for mm in mm_arr:
            
            print(yy,mm)
            
            # remove daily folder structure if yy is 2022
            #file_list = []
            #if yy == '2022':
            #    subfolders= [f.path for f in os.scandir(CM_SAF_path+yy+'/'+mm+'/') if f.is_dir()]
            #    for dir in subfolders:
            #        print(dir)
            #        files = (glob.glob(dir+'/*.nc'))
            #        file_list.append(files)
                
                
            #    file_list = list(itertools.chain.from_iterable(file_list))
            #    print(file_list)
                # moving files in the month subfolder
            #    [shutil.move(file_day, CM_SAF_path+yy+'/'+mm+'/') for file_day in file_list]

                
            
            # read CM_SAF CM data of the month 
            CM_saf = read_CM_SAF(CM_SAF_path+yy+'/'+mm+'/')
            
            print(CM_saf)
            
            # calculating mean cloud probability
            CP_mean = CM_saf.cma_prob.mean(dim='time', skipna=True)

            # calculating counts for cloud mask flag
            CC_count = CM_saf.cma.sum(dim='time')
            CC_count_norm = CC_count/np.nanmax(CC_count)
            
            # read lat/lon values
            lats, lons = read_lat_lon_CMSAF(CM_SAF_path) 

            # plot mean cloud prob
            #plot_cmsaf(lons,
            #        lats, 
            #        CP_mean, 
            #        yy+mm+"_cloud probability", 
            #        CMAP_an, 
            #        "Cloud probability", 
            #        domain_expats, 
            #        path_figs,
            #        'expats', 
            #        True, 
            #        0., 
            #        100.)
            
            # plot cloud counts
            plot_cmsaf(lons,
                    lats, 
                    CC_count_norm, 
                    yy+mm+"_cloud counts", 
                    CMAP_an, 
                    "Cloud counts", 
                    domain_dfg, 
                    path_figs,
                    'dfg', 
                    True, 
                    np.nanmin(CC_count_norm), 
                    np.nanmax(CC_count_norm))
            
            
def plot_cmsaf(lons, lats, variable, label, cmap, cbar_title, domain, path_out, key, back_transparent, vmin, vmax):
    """
    plot map of the variable over the defined domain

    Args:
        lons (array): longitude values
        lats (array): latitudes 
        variable (matrix): variable to plot
        label (string): string for plot filename
        cmap (colormap): color map 
        cbar_title (string): title for color bar
        domain (array): minlon, maxlon, minlat, maxlat
        path_out (string): path where to save the plot
        key (string): string possible "expats" or "dfg"
        back_transparent (boolean): True or False - true means transparent background
        vmin (float): value min in colorbar
        vmax (float): max value in colorbar
        
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
        BT_levels = np.linspace(np.nanmin(variable), np.nanmax(variable), 20) # scaled for zoomed region
        # plotting on the back, invisible in the end, the field for getting the colormap
        mesh_transp =  ax.contourf(lons, 
                        lats, 
                        variable,
                        transform=ccrs.PlateCarree(), 
                        levels=BT_levels, 
                        alpha=1.,
                        cmap=cmap, 
                        vmin=vmin, 
                        vmax=vmax)
        
        plt.colorbar(mesh_transp,
                     ax=[ax],
                     label=cbar_title, 
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
        var_levels = np.linspace(vmin, vmax, 20)
        # plot variable as filled contours
        mesh = ax.contourf(lons, 
                            lats, 
                            variable, 
                            cmap=cmap, 
                            transform=ccrs.PlateCarree(), 
                            levels=var_levels, 
                            vmin=vmin, # 230
                            vmax=vmax) # 270
        cbar = plt.colorbar(mesh, label=cbar_title, shrink=0.6)

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
        transparent=back_transparent,
        )

    plt.close()




if __name__ == "__main__":
    main()
        