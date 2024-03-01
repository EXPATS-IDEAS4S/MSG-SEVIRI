"""
code to test Inoue and Ahonashi criteria to detect precipitating regions over expats domain using their thresholds
"""

# theis and ahonashi
BTD_1112_thr = 1.5 # below threshold for rain
RATIO_0616_thr = 25 # abovee threshold for rain
BTD_3811_thr = 8 # below threshold for rain

# criteria 1
BT_11_thr_ch1 = 235 # single threshold --> below prec

# criteria 2
BT_11_thr_ch2 = 260.


# criteria 3
RATIO_0616_thr_ch3 = 25 # above 25 
BT_11_thr_ch3 = 260.

# criteria 4
RATIO_0616_thr_ch4 = 1.5 # above 25 
BT_11_thr_ch4 = 260.

# criteria 5
BTD_3811_thr_ch5 = 8 # below threshold for rain
BT_11_thr_ch5 = 260.

from readers.files_dirs import path_dir_tree, path_figs, path_features
from readers.msg_ncdf import feature_list
from readers.msg_ncdf import read_daily_ncdf_msg_channel, read_lat_lon_file, feature_list
from figures.mpl_style import CMAP, plot_cities_expats, plot_local_dfg
from figures.domain_info import domain_expats
import numpy as np
import xarray as xr
import os

def main():
    
    rain_crit = 'my_test'
    
    # read features for one day 
    date = '20230724'
    print(path_dir_tree)
    # read all features on the selected day
    data_day = read_features_day(path_features, date, feature_list)
    ch_108 = read_daily_ncdf_msg_channel(path_dir_tree, date, "IR_108")


    # add rain mask variable
    N, x, y = np.shape(data_day.BTD_6211.values) 


    rf = np.zeros((x,y))
    rf.fill(1)
    data_day = data_day.assign(rain_flag=(['x','y'],rf))
    data_day = data_day.assign(IR_108=(['time','x','y'],ch_108.IR_108.values))
    
    # cutting nighttime period 
    # input sunrise and sunset in CEST
    data_daytime = select_daytime(date, 5, 48, 20, 55, True, data_day)
    
    
    print(data_daytime.time.values[0], data_daytime.time.values[-1])
    print(np.where(data_day.time.values == data_daytime.time.values[0]))
    print(np.where(data_day.time.values == data_daytime.time.values[-1]))

    strasuka
    
    # apply rain criteria    
    if rain_crit == 'theis_anohashi':
        rain = data_daytime.where((data_daytime.BTD_3911 > 8.) *
                              (data_daytime.BTD_1112 < 1.5) * 
                              (data_daytime.RATIO_0616 > 0.25),
                              np.nan)
    elif rain_crit == '2':
        rain = data_daytime.where((data_daytime.IR_108 < 220), np.nan)  
        
    elif rain_crit == '3':
        rain = data_daytime.where((data_daytime.IR_108 < 235) * 
                              (data_daytime.RATIO_0616 > 0.25),
                              np.nan)   
        
    elif rain_crit == '4':       
        rain = data_daytime.where((data_daytime.IR_108 < 235) * 
                              (data_daytime.BTD_3911 > 30),
                              np.nan)
        
    elif rain_crit == '5':       
        rain = data_daytime.where((data_daytime.IR_108 < 235) * 
                              (data_daytime.BTD_1112 < 1.5),
                              np.nan)        
        
    elif rain_crit == 'my_test':
        rain = data_daytime.where((data_daytime.IR_108 < 235) * 
                              (data_daytime.BTD_1112 < 1.5) * 
                              (data_daytime.BTD_3911 > 30) * 
                              (data_daytime.RATIO_0616 > 0.25),
                              np.nan)            
    counts_rain = rain.count(dim='time')    
    
    norm_counts = counts_rain.rain_flag.values/N

    # plot map of occurrences of rain
    lons, lats = read_lat_lon_file()
    
    #plot_msg(lons, 
    #         lats, 
    #         norm_counts, 
    #         rain_crit, 
    #         CMAP,  
    #         'normalized rain occurrence', 
    #         domain_expats, 
    #         path_figs, 
    #         'expats', 
    #         True, 
    #         0., 
    #         1.)


    path_quicklooks = path_figs+'/'+date+'_quicklooks/'

    for i, time_stamp in enumerate(data_daytime.time.values):
        
        print(time_stamp)   
        # check if files exist already
        if not os.path.exists(path_quicklooks+'95_rain_crit_'+rain_crit+'_expats.png'):

            # selecting data of the time stamp
            ds_plot = data_daytime.isel(time=i)
            rain_plot = rain.isel(time=i)
            
            # call plotting script
            if len(str(i)) == 1:
                count = '0'+str(i)
            else:
                count = str(i)
                
            plot_msg_hatch_rain(lons, 
                     lats, 
                     ds_plot.IR_108.values, 
                     rain_plot,
                     count+'_rain_crit', 
                     CMAP, 
                     'IR 10.8 $mu$m ', 
                     domain_expats, 
                     path_quicklooks, 
                     rain_crit+'_expats', 
                     False, 
                     200., 
                     310.)
            
    if not os.path.exists(path_quicklooks+'/gifs/'+date+'_rain_crit_'+rain_crit+'.gif'):
        # create animated gif of list of plots
        gif_maker(path_quicklooks, 
                  date+'_rain_crit_'+rain_crit, 
                  path_quicklooks+'/gifs/', 
                  250, 
                  rain_crit)
            
    
    
def read_features_day(path_files, date, f_list):
    
    from datetime import datetime
    import glob
    import xarray as xr
    
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    
    features = []
    for i, feature in enumerate(f_list):
    
        # read daily file
        data = xr.open_dataset(path_files+'/'+yy+mm+'_'+feature+'_MSG_SEVIRI_EXPATS.nc')
        # selecting day
        date_start = datetime(int(yy), int(mm), int(dd), 0, 0, 0)
        date_end = datetime(int(yy), int(mm), int(dd), 23, 59, 59)

        data_day = data.sel(time=slice(date_start, date_end))
        data_day = data_day.rename({'feature':feature})

        features.append(data_day)
    
    ds = xr.merge(features)
    return ds


def select_daytime(date, sr_hh, sr_mm, ss_hh, ss_mm, summer, data):
    """
    function to calcuulate sunrise and sunset in UTC and slice the dataset 

    Args:
        date (string): _description_
        sr_hh (int): _description_
        sr_mm (int): _description_
        ss_hh (int): _description_
        ss_mm (int): _description_
        summer (boolean): _description_
        data (xarray dataset): _description_

    Returns:
        xarray dataset: dataset sliced for daytime
    """
    from datetime import datetime
    yy = date[0:4]
    mm = date[4:6]
    dd = date[6:8]
    
    if summer == True:
        sunrise_time = datetime(int(yy), int(mm), int(dd), sr_hh-2, sr_mm, 0)
        sunset_time = datetime(int(yy), int(mm), int(dd), ss_hh-2, ss_mm, 0)
    else:
        sunrise_time = datetime(int(yy), int(mm), int(dd), sr_hh-1, sr_mm, 0)
        sunset_time = datetime(int(yy), int(mm), int(dd), ss_hh-1, ss_mm, 0)
 
    data = data.sel(time=slice(sunrise_time, sunset_time))
    
    
    return data
    

    
def gif_maker(image_folder, gif_name, gif_path, gif_duration, channel):
    """
    script to create animated gif from a folder containing images

    Args:
        image_folder (string): folder containing png images
        gif_name (string): string as filename for gif
        gif_path (string): path for gif file
        gif_duration (int): duration for gif (typical 250)
        channel(string): variable string for the gif
        
    """
    from PIL import Image
    import glob
    
    import matplotlib.pyplot as plt
    

    
    # read files into the fil elist
    image_array = []
    
    for file in sorted(glob.glob(f'{image_folder}/*_rain_crit_'+channel+'_expats.png')):
                
        image = Image.open(file)
        image_array.append(image)

    print(image_array)
    im = image_array[0]            
    im.save(gif_path+gif_name+".gif", 
            format='png',
            save_all=True, 
            append_images=image_array, 
            duration=gif_duration, 
            loop=0)
    

    
    return


def plot_msg_hatch_rain(lons, lats, variable, rain, label, cmap, cbar_title, domain, path_out, key, back_transparent, vmin, vmax):
    """
    plot map of the variable over the defined domain

    Args:
        lons (array): longitude values
        lats (array): latitudes 
        variable (matrix): variable to plot
        rain (matrix): rain criteria for hatching
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
    import matplotlib.pyplot as plt
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature


    
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
    
    var_levels = np.linspace(vmin, vmax, 20)

    mesh = ax.contourf(lons, 
                        lats, 
                        variable, 
                        cmap=cmap, 
                        transform=ccrs.PlateCarree(), 
                        levels=var_levels, 
                        vmin=vmin, # 230
                        vmax=vmax) # 270
    
    rain_mask = np.ma.masked_where(rain.rain_flag.values == 1, rain.rain_flag.values)
    ax.pcolor(lons, 
              lats,
              rain.rain_flag.values, 
              transform=ccrs.PlateCarree(),
              hatch='**',
              color='white', 
              alpha=0.2)    
    
    
    
    cbar = plt.colorbar(mesh, label=cbar_title, shrink=0.6)

    ax.add_feature(cfeature.LAKES)
    ax.add_feature(cfeature.RIVERS)
    
    plt.tick_params(axis='both',which='major',labelsize=14)

    ax.set_xlabel('Latitude [$^{\circ}$]')
    ax.set_ylabel('Longitude [$^{\circ}$]')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)


    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=1.5, color='black')
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
        