import sys
import xarray as xr
import matplotlib.colors as mcolors
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

sys.path.append('/home/dcorradi/Documents/Codes/MSG-SEVIRI/')
from figures.plotting_functions import plot_single_map, calc_channels_max_min

orography_path = "/net/ostro/figs_proposal_TEAMX/orography_expats_high_res.nc"
path_output = "/work/case_studies_expats/"

ds = xr.open_dataset(orography_path)
print(ds)

orography = ds['orography'].values
lats = ds['lats'].values
lons = ds['lons'].values

# Load the original terrain colormap
# terrain_cmap = plt.cm.get_cmap('terrain')

# # Choose the start point to skip the blue part, e.g., 0.25 means starting from 25% of the original colormap,
# # effectively skipping the first quarter which includes the blues.
# start = 0.25
# stop = 1.0

# # Create a new colormap without the blue part
# colors = terrain_cmap(np.linspace(start, stop, 256))
# cmap = LinearSegmentedColormap.from_list('no_blue_terrain', colors)
# cmap = 'terrain'

terrain_cmap = plt.get_cmap('terrain')
newcolors = terrain_cmap(np.linspace(0.25, 1, 256))  # Skipping blue gradients
blue = np.array([0, 0, 1, 1])  # RGBA for blue
newcolors[:25, :] = blue  # Assign blue to the lowest values (assuming these represent sea level and below)
cmap = mcolors.ListedColormap(newcolors)

vmin, vmax = calc_channels_max_min(['orography'],ds)
norm = mcolors.Normalize(vmin=vmin[0], vmax=vmax[0])
#norm = mcolors.PowerNorm(gamma=0.4)
lonmin, latmin, lonmax, latmax= 5, 42, 16, 51.5

plot_single_map(orography,lons,lats,cmap,norm,[lonmin,lonmax,latmin,latmax],'EXPATS','orography','elevation (m)',path_output) #[left, right, bottom ,top]


