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
import sys

#methods for regridding
sys.path.append('/home/dcorradi/Documents/Codes/MSG-SEVIRI/process/')
from regrid_functions import generate_regular_grid, regrid_data, fill_missing_data_with_interpolation

# Define the file path 
#path_to_file = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_Flood_domain_DataTailor_nat/" 
path_to_file = "/work/case_studies_expats/Germany_Flood_2021/data/MSG/MSGNATIVE/"
#path_to_cth = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/" 
path_to_cth = "/work/case_studies_expats/Germany_Flood_2021/data/cloud_products/CTH_NWCSAF/NWC_SAF/"

# MSG file  
natfile = path_to_file+"MSG4-SEVI-MSG15-0100-NA-20210714122743.591000000Z-NA.subset.nat"

# CTH file 
cth_file = path_to_cth+"S_NWC_CTTH_MSG4_FLOOD-GER-2021-VISIR_20210714T121500Z.nc"
#cth_file = path_to_cth+"CM_SAF/CTXin20210714120000405SVMSGI1UD.nc"

# Fig Path
#path_to_fig = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/Fig/Parallax_Correction/"
path_to_fig = "/work/case_studies_expats/Germany_Flood_2021/Fig/"

# Define Domain
domain = lonmin, latmin, lonmax, latmax= 5, 48, 9, 52 #2021 Germany Flood Area

#Flag for regridding
regrid = True

# Define Time
date_time_str = cth_file.split('.')[0].split('_')[-1]
#date_time_str = cth_file.split('.')[0].split('/')[-1][5:17]

# Convert the string to a datetime object
#date_time_obj = datetime.strptime(date_time_str, '%Y%m%d%H%M%S')
date_time_obj = datetime.strptime(date_time_str, '%Y%m%dT%H%M%SZ')

# Format the datetime object into a more readable string. For example, "July 12, 2021, 00:00"
readable_date_time = date_time_obj.strftime('%d-%m-%Y, %H:%M')
print(readable_date_time)

# list of channels name
channels = ['IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']
channels_unit = ['Reflectances (%)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Reflectances (%)', 'Reflectances (%)', 'Brightness Temperature (K)', 'Brightness Temperature (K)']

#open msg files without parrallax
scn = satpy.Scene(reader='seviri_l1b_native', filenames=[natfile])
#scn_cth = satpy.Scene(reader='cmsaf-claas3_l2_nc', filenames=[cth_file])
#scn_cth = satpy.Scene(reader='nwcsaf-geo', filenames=[cth_file])

#open msg files with parrallax
#scn_parallax = satpy.Scene({"seviri_l1b_native": [natfile], "cmsaf-claas3_l2_nc": [cth_file]})
scn_parallax = satpy.Scene({"seviri_l1b_native": [natfile], "nwcsaf-geo": [cth_file]})

for i,ch in enumerate(channels):
    #Load channel
    scn.load([ch])       

    #Crop to area of interest
    crop_scn = scn.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

    #get data in the cropped area
    sat_data_crop = crop_scn[ch].values #R/Tb
    print('sat data',np.shape(sat_data_crop), sat_data_crop)

    #get coord in the cropped area
    area_crop = crop_scn[ch].attrs['area'] #area in m
    sat_lon_crop, sat_lat_crop = area_crop.get_lonlats() #lat/lon grid
    print('sat lon data',np.shape(sat_lon_crop), sat_lon_crop)
    print('sat lat data',np.shape(sat_lat_crop), sat_lat_crop) 
    
    # Apply the Parallax Correction
    
    ch_parallax = 'parallax_corrected_'+ch

    scn_parallax.load([ch_parallax])

    #Crop to area of interest
    crop_scn_parallax = scn_parallax.crop(ll_bbox=(lonmin, latmin, lonmax, latmax))

    #get data in the cropped area
    sat_data_crop_parallax = crop_scn_parallax[ch_parallax].values #R/Tb
    print('sat data parallax',np.shape(sat_data_crop_parallax),sat_data_crop_parallax)

    #get coord in the cropped area
    area_crop_parallax = crop_scn_parallax[ch_parallax].attrs['area'] #area in m
    sat_lon_crop_par, sat_lat_crop_par = area_crop_parallax.get_lonlats() #lat/lon grid 
    print('sat lon data parallax',np.shape(sat_lon_crop_par), sat_lon_crop_par)
    print('sat lat data parallax',np.shape(sat_lat_crop_par), sat_lat_crop_par)

    if regrid:
        #fill missing values with interpolation
        sat_data_crop_par = fill_missing_data_with_interpolation(sat_lat_crop_par, sat_lon_crop_par, sat_data_crop_parallax)
        
        #find regular lat lon points
        lat_arr,  lon_arr = generate_regular_grid(latmin,latmax,lonmin,lonmax,0.03,path_to_file)
        print(lat_arr,lon_arr)
    
        # Generate grid points
        sat_lat_crop_reg, sat_lon_crop_reg = np.meshgrid(lat_arr, lon_arr, indexing='ij')
        print('sat lon data reg grid',np.shape(sat_lon_crop_par), sat_lon_crop_par)
        print('sat lat data reg grid',np.shape(sat_lat_crop_par), sat_lat_crop_par)        

        #regrid
        sat_data_crop_parallax = regrid_data(sat_lat_crop_par, sat_lon_crop_par, sat_data_crop_par, sat_lat_crop_reg, sat_lon_crop_reg)
        print('sat data reg grid',np.shape(sat_data_crop_parallax),sat_data_crop_parallax)

    #plot sat data with and without parallax correction
    #TODO include also the CTH in the background

    # Plotting setup
    fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(15, 10), subplot_kw={'projection': ccrs.PlateCarree()})  # Two subplots

    if channels_unit[i]=='Brightness Temperature (K)':
        cmap = 'cool'
    elif channels_unit[i]=='Reflectances (%)':
        cmap = 'gray'

    sat_min = np.amin(sat_data_crop)
    sat_max = np.amax(sat_data_crop)
    norm = colors.Normalize(vmin=sat_min, vmax=sat_max)

    # Create a ScalarMappable with the normalization and colormap
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])

    # Plot
    axs[0].contourf(sat_lon_crop, sat_lat_crop, sat_data_crop, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
    axs[0].set_title('No Parallax Correction')
    if regrid:
        axs[1].contourf(sat_lon_crop_reg, sat_lat_crop_reg, sat_data_crop_parallax, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
        axs[1].set_title('With Parallax Correction and regrid')
    else:
        axs[1].contourf(sat_lon_crop_par, sat_lat_crop_par, sat_data_crop_parallax, transform=ccrs.PlateCarree(), norm=norm, cmap=cmap)
        axs[1].set_title('With Parallax Correction')

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
        ax.set_extent([5, 9, 48, 52])  # Adjust this based on your data
        #ax.set_extent([4.5, 9.5, 47.5, 52.5])

    # Add a title to the figure
    plt.suptitle('Channel '+ch+' - '+readable_date_time, fontsize=14, fontweight='bold',y=0.77)

    #plt.show()
    # Uncomment the line below to save the figure
    if regrid:
       fig.savefig(path_to_fig+'par_corr_regrid_maps_'+ch+'_'+date_time_str+'.png', bbox_inches='tight')
    else:
        fig.savefig(path_to_fig+'par_corr_maps_'+ch+'_'+date_time_str+'.png', bbox_inches='tight')
    plt.close()