"""
plot one day gif of all channels to see what is in the data 
"""



from readers.files_dirs import path_dir_tree, path_figs, path_features
from readers.msg_ncdf import read_daily_ncdf_msg_channel, read_daily_feature_msg_channel, ch_list, read_lat_lon_file, ch_min_list, ch_max_list, feature_list, f_max_list, f_min_list
from figures.domain_info import domain_expats, domain_dfg

from figures.mpl_style import CMAP, plot_cities_expats, plot_local_dfg

import xarray as xr
import matplotlib.pyplot as plt
import os
import numpy as np
from fig01_distr_expats import plot_msg


def main():
    
    
    
    # read data of the month of july
    date = '20230724'
    # select channel to read
    # ch_list = ['IR_108', 'IR_039', 'IR_016', 'IR_087', 'IR_097', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']

    #channel = ch_list[10]
    #vmin = ch_min_list[10]
    #vmax = ch_max_list[10]
    
    #feature_list = ['BTD_3911', 'BTD_6211', 'BTD_1112', 'BTD_8711', 'RATIO_0616']
    channel = feature_list[-1]
    vmin = f_min_list[-1]
    vmax = f_max_list[-1]
    print(vmin, vmax)
    
    # feature title
    cbar_title = channel+'$mu$m, [K]'
    #data = read_daily_ncdf_msg_channel(path_dir_tree, date, channel)

    data = read_daily_feature_msg_channel(path_features, date, channel)

    # create folder for each plot 
    path_quicklooks = path_figs+'/'+date+'_quicklooks/'
    os.makedirs(path_quicklooks, exist_ok=True)    
    
    
    # select channel to plot from channel list

    # read lat lons variables
    lons, lats = read_lat_lon_file()


    for i, time_stamp in enumerate(data.time.values):
        
        print(time_stamp)   
        # check if files exist already
        if not os.path.exists(path_quicklooks+'95_'+channel+'_expats.png'):

            # selecting data of the time stamp
            ds_plot = data.isel(time=i)
            
            # call plotting script
            if len(str(i)) == 1:
                count = '0'+str(i)
            else:
                count = str(i)
                
            plot_msg(lons, 
                     lats, 
                     ds_plot[channel].values, 
                     count+'_'+channel, 
                     CMAP, 
                     cbar_title, 
                     domain_expats, 
                     path_quicklooks, 
                     'expats', 
                     False, 
                     vmin, 
                     vmax)

    if not os.path.exists(path_quicklooks+'/gifs/'+date+'_'+channel+'.gif'):
        # create animated gif of list of plots
        gif_maker(path_quicklooks, date+'_'+channel, path_quicklooks, 250, channel)
            
    
    
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
    
    for file in sorted(glob.glob(f"{image_folder}/*"+channel+'_expats.png')):
                
        image = Image.open(file)
        image_array.append(image)

    im = image_array[0]            
    im.save(gif_path+gif_name+".gif", 
            format='png',
            save_all=True, 
            append_images=image_array, 
            duration=gif_duration, 
            loop=0)
    

    
    return


    
if __name__ == "__main__":
    main()
        