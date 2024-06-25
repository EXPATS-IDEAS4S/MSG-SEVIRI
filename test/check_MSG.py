import satpy 
import datetime
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
from datetime import datetime
import matplotlib.cm as cm
import matplotlib.colors as colors

# Define the file path 
path_to_file = "/data/sat/msg/nat/2015/04/30/"

# Define MSG series number
msg1 = '1'
msg3 = '3'

# MSG file  
natfile1 = path_to_file+f"MSG{msg1}-SEVI-MSG15-0100-NA-20150430131242.579000000Z-NA.subset.nat"
natfile2 = path_to_file+f"MSG{msg3}-SEVI-MSG15-0100-NA-20150430131240.588000000Z-NA.subset.nat"

# Fig Path
path_to_fig = "/data/sat/msg/nat/figs/"

# Define Domain
domain = lonmin, latmin, lonmax, latmax= 5, 42, 16, 51.5 #Expats

date_time_str = natfile1.split('-')[5].split('.')[0]
 
# Convert the string to a datetime object
date_time_obj = datetime.strptime(date_time_str, '%Y%m%d%H%M%S')

# Format the datetime object into a more readable string. For example, "July 12, 2021, 00:00"
readable_date_time = date_time_obj.strftime('%d-%m-%Y, %H:%M')
print(readable_date_time)

# list of channels name
channels = ['IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']
channels_unit = ['Reflectances (%)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Reflectances (%)', 'Reflectances (%)', 'Brightness Temperature (K)', 'Brightness Temperature (K)']

#open msg files without parrallax
scn1 = satpy.Scene(reader='seviri_l1b_native', filenames=[natfile1])
scn2 = satpy.Scene(reader='seviri_l1b_native', filenames=[natfile2])


for i,ch in enumerate(channels):
    #Load channel
    scn1.load([ch])  
    scn2.load([ch])     

    #Crop to area of interest
    crop_scn1 = scn1.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))
    crop_scn2 = scn2.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

    #get data in the cropped area
    sat_data_crop1 = crop_scn1[ch].values #R/Tb
    print(f'sat data MSG{msg1}',np.shape(sat_data_crop1), sat_data_crop1)
    sat_data_crop2 = crop_scn2[ch].values #R/Tb
    print(f'sat data MSG{msg3}',np.shape(sat_data_crop2), sat_data_crop2)

    #get coord in the cropped area
    area_crop1 = crop_scn1[ch].attrs['area'] #area in m
    sat_lon_crop1, sat_lat_crop1 = area_crop1.get_lonlats() #lat/lon grid
    print(f'sat lon data MSG{msg1}',np.shape(sat_lon_crop1), sat_lon_crop1)
    print(f'sat lat data MSG{msg3}',np.shape(sat_lat_crop1), sat_lat_crop1) 

    area_crop2 = crop_scn2[ch].attrs['area'] #area in m
    sat_lon_crop2, sat_lat_crop2 = area_crop2.get_lonlats() #lat/lon grid
    print(f'sat lon data MSG{msg1}',np.shape(sat_lon_crop2), sat_lon_crop2)
    print(f'sat lat data MSG{msg3}',np.shape(sat_lat_crop2), sat_lat_crop2)

    # Plotting setup for the maps
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15, 10), subplot_kw={'projection': ccrs.PlateCarree()})  # Two subplots

    if channels_unit[i]=='Brightness Temperature (K)':
        cmap = 'cool'
    elif channels_unit[i]=='Reflectances (%)':
        cmap = 'gray'

    sat_min = np.amin(sat_data_crop1)
    sat_max = np.amax(sat_data_crop1)
    norm = colors.Normalize(vmin=sat_min, vmax=sat_max)

    # Create a ScalarMappable with the normalization and colormap
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    # Plot
    axs[0].contourf(sat_lon_crop1, sat_lat_crop1, sat_data_crop1, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
    axs[0].set_title(f'MSG {msg1}')

    axs[1].contourf(sat_lon_crop2, sat_lat_crop2, sat_data_crop2, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
    axs[1].set_title(f'MSG {msg3}')

    # Add color bar
    fig.colorbar(sm, ax=axs, orientation='vertical', label=channels_unit[i], shrink=0.6, pad=0.02)

    # Loop through each subplot
    for ax in axs:
        # Set axis tick labels
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                        linewidth=0.75, color='yellow', alpha=0.6, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        #gl.xlines = 
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {'size': 10, 'color': 'black'}
        gl.ylabel_style = {'size': 10, 'color': 'black'}

        # Adds coastlines and borders to the current axes
        ax.coastlines(resolution='50m', linewidths=0.5)
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='black')
        ax.set_extent([lonmin, lonmax, latmin, latmax])  # Adjust this based on your data

    # Add a title to the figure
    plt.suptitle('Channel '+ch+' - '+readable_date_time, fontsize=14, fontweight='bold',y=0.77)

    #plt.show()
    fig.savefig(path_to_fig+f'MSG-{msg1}-{msg3}_maps_'+ch+'_'+date_time_str+'.png', bbox_inches='tight')
    plt.close()


    # Plotting setup for the distributions
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(12, 10))  # Two subplots

    #create bins
    sat_min = np.amin(sat_data_crop1)
    sat_max = np.amax(sat_data_crop1)
    bin_width = 2
    bins = np.arange(sat_min, sat_max + bin_width, bin_width)

    # Plot
    axs[0].hist(sat_data_crop1.flatten(), bins=bins, color='blue', alpha=0.7, density=True)
    axs[0].set_title(f'MSG {msg1}')
    axs[0].set_xlabel(channels_unit[i])

    axs[1].hist(sat_data_crop2.flatten(), bins=bins, color='blue', alpha=0.7, density=True)
    axs[1].set_title(f'MSG {msg3}')
    axs[1].set_xlabel(channels_unit[i])

    # Add a title to the figure
    plt.suptitle('Channel '+ch+' - '+readable_date_time, fontsize=14, fontweight='bold',y=0.9)

    #plt.show()
    fig.savefig(path_to_fig+f'MSG-{msg1}-{msg3}_distr_'+ch+'_'+date_time_str+'.png', bbox_inches='tight')
    plt.close()

