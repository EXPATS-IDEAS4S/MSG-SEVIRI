# %%
import numpy as np
import os
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs                   # import projections
import cartopy.feature as cfeature           # import features
import uuid
from scipy import interpolate
import scipy.io
from glob import glob
import os
from matplotlib.offsetbox import AnchoredText
from matplotlib.patches import Rectangle

### constants taken from www-cdn.eumetsat.int/files/2020-04/pdf_effect_rad_to_brightness.pdf
scale_factor = 0.2050356762076601
add_offset = -10.456819486590666
kB = 1.3806488*10**(-23)   ## Boltzmann constant [J/K]
h = 6.62606957*10**(-34) ## Planck constant [J*s]
c = 299792458         ## speed of light [m/s]
## lambda <- 10.8 * 10^(-6)  ## [µm] to [m]
vc = 930.647 ## [1/cm]; for IR 10.8 channel Meteosat 8 (MSG FM-1); Table 7.2 doc^^
vcm = vc * 100 ## [1/m] conversion of the wavenumber in SI units
alpha = 0.9983  ## [] dimensionless, Table 7.2
beta = 0.625   ## [K]; Table 7.2
c1  = 2*h*c**2 ## [J*m^2/s] = [Wm2]
c2 = h*c/kB ## [K*m]

# %%
def plot_msg(lons, lats, variable, label, cmap='Greys', vmin=None, vmax=None, title=None, path_out=None):
    # Plot the map of MSG channels vs lat/lon
    fig = plt.figure(figsize=(10,10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax.spines["top"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)
    ax.set_extent(extent_param)
    if title is not None:
        ax.set_title(title)

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True, alpha=0.5)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'fontsize': 14}
    gl.ylabel_style = {'fontsize': 14}

    pc = ax.pcolormesh(lons,lats,variable, cmap=cmap, vmin=vmin if vmin is not None else np.min(variable), 
                       vmax=vmax if vmax is not None else np.max(variable))
    #vmin, vmax=220.,
    plt.tick_params(axis='both',which='major',labelsize=14)

    ax.set_xlabel('Latitude [$^{\circ}$]')
    ax.set_ylabel('Longitude [$^{\circ}$]')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)
    cbar = plt.colorbar(pc,ax=ax,shrink=0.75)
    cbar.set_label(label,fontsize=14)
    cbar.ax.tick_params(labelsize=14)

    ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=0.5, color='orange')
    ax.add_feature(cfeature.STATES, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=1., color='orange')

    if path_out is not None:
        plt.savefig(path_out, bbox_inches='tight', transparent=True)
        print('file saved')
    plt.show()
    plt.close()


# %%
######### data in /net/ostro #############
#datapath = '/net/ostro/'
#folder = '20210708_hail_Italy_alps'
#folder = '20210726_hail_Lombardia'
#folder = '20210628_hail_switzerland_South_ger'
##########################################

######### data in /data/trade_pc/MSG_severe_cases/ #############
datapath = '/data/trade_pc/MSG_severe_cases/'
#folder = '20210629_hail_alps_central_eu'
folder = '20210726_hail_southger_northIta'
################################################################

# reading file list
path_files = datapath+folder+'/'
print(path_files)
file_list = np.sort(glob(path_files+'/*.nc'))
print(len(file_list))

# define area
area_str = 'IDEA-S4S'; area_name = 'Alpine domain'
minlon = 5.; maxlon = 16.; minlat = 42.; maxlat = 51.5
# smaller domain which Paula used plotting DCs data
# minlon = 5.; maxlon = 16.; minlat = 44.5; maxlat = 49.5
extent_param = [minlon, maxlon, minlat, maxlat]


# %%
for file_path in file_list:
    # extracting date from the string
    datetime_str = os.path.basename(file_path).split('_')[-1][:14]
    year = datetime_str[:4]
    month = datetime_str[4:6]
    day = datetime_str[6:8]
    hours = datetime_str[8:10]
    minutes = datetime_str[10:12]
    seconds = datetime_str[12:]

    print(f"{year}-{month}-{day}, {hours}:{minutes}:{seconds}")
    with xr.open_dataset(file_path) as dataset:
        # Read the longitude and latitute.
        lons = dataset.lon.values
        lats = dataset.lat.values

        # calculate radiances at 10.8 microns
        #rad_ch_108 = add_offset + (msg_data.ch9.values * scale_factor) # radiance in mW m-2 sr-1(cm-1)-1
        # converting the radiance in SI standard ( W/m-1/sr)
        rad_108_MKS = dataset.ch9.values*10**(-5)  # radiance in W m-1 sr-1

        # converting radiance to brightness temperature [ in K]
        numerator = c2*vcm
        fraction = c1*(vcm**3)/rad_108_MKS
        denominator = alpha * (np.log(fraction))
        TB_108 = numerator/denominator - beta/alpha  ## [K]
        print(np.nanmax(TB_108), np.nanmin(TB_108), np.nanmean(TB_108))

        # figure_path_out = path_out+date[0:8]+'_'+num+'.png'
        plot_msg(lons, lats, TB_108, 'Brightness temperature [K]', cmap='Greys', vmin=None, vmax=None,
                 title=f"{year}-{month}-{day}, {hours}:{minutes}:{seconds}", path_out=None)

# %%
