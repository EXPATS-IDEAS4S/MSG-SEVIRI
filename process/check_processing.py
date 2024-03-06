"""
Check the quality of the different steps performed during the MSG processing
like parallax correction, interpolation of missing values and regridding
TODO: plot also the CTH in the background

@author: Daniele Corradini
"""

import xarray as xr
from glob import glob
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np
import matplotlib.colors as colors
import os

#Import parameters from config file and custom methods
from config_satpy_process import path_to_file, path_to_cth, path_fig, cth_file
from config_satpy_process import lonmin, lonmax, latmax, latmin, channels, channels_unit, channels_cmaps

#methods for visualizing data and checking quality
sys.path.append('/home/dcorradi/Documents/Codes/MSG-SEVIRI/figures/')
from plotting_functions import set_map_plot, calc_channels_max_min

#file patterns
msg_file_pattern = 'MSG4-SEVI-MSG15-0100-NA-*.nc' #MSG4-SEVI-MSG15-0100-NA-20210715232743.nc
msg_file_pattern_regrid = 'MSG4-SEVI-MSG15-0100-NA-*_regular_grid.nc' #MSG4-SEVI-MSG15-0100-NA-20210712031244_regular_grid.nc

#get list of file names
fnames = sorted(glob(path_to_file+'Processed/'+msg_file_pattern))
fnames_pc = sorted(glob(path_to_file+'Parallax_Corrected/'+msg_file_pattern))
fnames_pc_reg = sorted(glob(path_to_file+'Parallax_Corrected/'+msg_file_pattern_regrid))
fnames_pc = sorted(list(set(fnames_pc) - set(fnames_pc_reg)))
n_files = len(fnames)
print(f'Processing {n_files} files')

#calculate max and min for each channel
ds_all_time = xr.open_mfdataset(fnames)
#print(ds_all_time)
chs_min, chs_max = calc_channels_max_min(channels, ds_all_time)
#print(chs_min,chs_max)

#open the nc file one at time for plotting maps
for i in range(n_files):
    if 100<=i<=200:
        print(f'opening nc file {i+1}/{n_files}')
        #open file without processing
        nc_file = xr.open_dataset(fnames[i])
        #print(nc_file)
        lat_grid = nc_file.variables['lat grid'].values.squeeze()
        lon_grid = nc_file.variables['lon grid'].values.squeeze()
        time = nc_file.coords['end_time'].values.squeeze()
        time = str(time).split('.')[0] #datetime.datetime.strptime(str(time), "%Y%m%d%H%M%S")
        print(time)
        #print(np.shape(lat_grid),lon_grid,lat_grid)

        #open file with parallax correction
        nc_file_pc = xr.open_dataset(fnames_pc[i])
        #print(nc_file_pc)
        lat_grid_pc = nc_file_pc.variables['lat_grid'].values.squeeze()
        lon_grid_pc = nc_file_pc.variables['lon_grid'].values.squeeze()
        #print(np.shape(lon_grid_pc),lon_grid_pc,lat_grid_pc)

        #open file with regrid
        nc_file_pc_reg = xr.open_dataset(fnames_pc_reg[i])
        #print(nc_file_pc_reg)
        lat = nc_file_pc_reg.coords['lat'].values
        lon = nc_file_pc_reg.coords['lon'].values
        lat_grid_pc_reg, lon_grid_pc_reg = np.meshgrid(lat,lon, indexing='ij')
        #print(np.shape(lon_grid_pc_reg),lon_grid_pc_reg,lat_grid_pc_reg)

        for j,ch in enumerate(channels):
            #get channel data
            data = nc_file.variables[ch].values.squeeze()
            data_pc = nc_file_pc.variables[ch].values.squeeze()
            data_pc_reg = nc_file_pc_reg.variables[ch].values.squeeze()

            # Create a figure and a set of subplots
            fig = plt.figure(figsize=(18, 5))
            
            # adjust with the actual max min over all the images
            norm = colors.Normalize(vmin=chs_min[j], vmax=chs_max[j]) 

            # Plot data on each subplot
            ax1 = fig.add_subplot(1,3,1,projection=ccrs.PlateCarree())
            ax1.contourf(lon_grid, lat_grid, data, transform=ccrs.PlateCarree(), norm=norm, cmap=channels_cmaps[j])  
            set_map_plot(ax1, norm, channels_cmaps[j], [lonmin, lonmax, latmin ,latmax], 'not processed', channels_unit[j])

            ax2 = fig.add_subplot(1,3,2,projection=ccrs.PlateCarree())
            ax2.contourf(lon_grid_pc, lat_grid_pc, data_pc, transform=ccrs.PlateCarree(), norm=norm, cmap=channels_cmaps[j])  
            set_map_plot(ax2, norm, channels_cmaps[j], [lonmin, lonmax, latmin ,latmax], 'parallax correction', channels_unit[j])

            ax3 = fig.add_subplot(1,3,3,projection=ccrs.PlateCarree())
            ax3.contourf(lon_grid_pc_reg, lat_grid_pc_reg, data_pc_reg, transform=ccrs.PlateCarree(), norm=norm, cmap=channels_cmaps[j])  
            set_map_plot(ax3, norm, channels_cmaps[j], [lonmin, lonmax, latmin ,latmax], 'regular grid', channels_unit[j])

            # Set an overall title for the figure
            fig.suptitle('MSG Processing Workflow - '+ch+'- '+str(time), fontsize=16, fontweight='bold')

            # Adjust the spacing at the top of the figure to make room for the overall title
            fig.subplots_adjust(top=0.90)

            #Display the figure with the subplots and Adjust layout to make room for titles and labels
            #plt.tight_layout()
            #plt.show()

            # Construct the full path for the directory
            directory = os.path.join(path_fig, ch)

            # Check if the directory exists, and create it if it does not
            if not os.path.exists(directory):
                os.makedirs(directory)

            # Save the figure
            fig.savefig(os.path.join(directory, f'MSE_processing_workflow_{ch}_{str(time).replace(" ", "_")}.png'), bbox_inches='tight')
            plt.close()
            print(f'Fig saved for channel {ch}')