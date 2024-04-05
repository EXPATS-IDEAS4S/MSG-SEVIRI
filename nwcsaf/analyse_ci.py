import xarray as xr
from glob import glob
import sys
import pandas as pd
import matplotlib.colors as mcolors
from matplotlib.patches import Patch
import numpy as np
import matplotlib.pyplot as plt


sys.path.append('/home/dcorradi/Documents/Codes/NIMROD/')
#from readers.read_functions import 
from figures.plot_functions import set_map_plot, plot_ci, plot_ci_flag_distribution
from figures.quality_check_functions import create_gif_from_folder

#Define paths and filepatter
ci_folder = "/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/"
ci_filepattern = "S_NWC_CI_MSG3_EXPATS-VISIR_*.nc"

fig_folder = "/work/dcorradi/case_studies_expats/Hailstorm_July_2023/fig/CI/"

#list of all MSG data
fnames_ci = sorted(glob(ci_folder+ci_filepattern))
print(fnames_ci)


def add_time_from_attr(ds):
    # Assuming 'nominal_product_time' is the attribute holding the desired time info
    # And it's in a format that pandas can parse to a datetime, e.g., "YYYY-MM-DD HH:MM:SS"
    nominal_time = pd.to_datetime(ds.attrs['nominal_product_time'])
    
    # Add it as a coordinate (assuming your data can be broadcasted against this single time value)
    ds = ds.assign_coords(time=nominal_time)
    
    # Ensure 'time' is a dimension if it isn't already one in your dataset
    if 'time' not in ds.dims:
        ds = ds.expand_dims('time')
    
    return ds

# Use open_mfdataset with the preprocess function
ds_combined = xr.open_mfdataset(fnames_ci, preprocess=add_time_from_attr, combine='nested', concat_dim='time')

# Check the result
print(ds_combined)

ci_probs_var=['ci_prob30', 'ci_prob60', 'ci_prob90']

#set plotting par
#0: no probability; 1: 0-25% probability; 2: 25-50% probability; 3: 50-75% probability; 4: 75-100% probability
lonmin, lonmax, latmin, latmax = 5. , 16. , 43. , 51.5
cmap = mcolors.ListedColormap(['white', 'lightskyblue', 'palegreen', 'orange', 'red' ])
bounds = [-0.5, 0.5, 1.5, 2.0, 2.5, 3.0]
norm = mcolors.BoundaryNorm(bounds, cmap.N)

# Add a legend for cloud mask
legend_labels = [Patch(facecolor='white', edgecolor='black', label='0%'),
                     Patch(facecolor='lightskyblue', edgecolor='black', label='0-25%'),
                     Patch(facecolor='palegreen', edgecolor='black', label='25-50%'),
                     Patch(facecolor='orange', edgecolor='black', label='50-75%'),
                     Patch(facecolor='red', edgecolor='black', label='75-100%'),]

"""
for file in fnames_ci:
    #open a single file
    ds = xr.open_dataset(file)
    lat=ds['lat'].values
    lon=ds['lon'].values
    time=ds.attrs['nominal_product_time']
    plot_ci(ds, lat, lon, time, ci_probs_var, [lonmin, lonmax, latmin, latmax], cmap, norm, legend_labels, fig_folder)
"""

#create gif
create_gif_from_folder(fig_folder+'maps/',fig_folder + 'CI_hailstorm2023.gif')

flag_values = [0, 1, 2, 4, 8, 16, 32]
flag_meanings = ['not_processed','High_resolution_satellite_data_used','Visible_data_used','IR3.9m_data_used','Cloud_type_data_used','Cloud_Microphysic_data_used','NWP_data_used']

flag_values_conditions = [1, 2, 4, 6, 8, 16, 32, 48, 64, 128, 256, 512, 768, 1024, 2048, 3072, 4096, 8192, 12288, 16384, 32768, 49152]
flag_meanings_conditions = ["space", "night", "day", "twilight", "sunglint", "land", "sea", "coast", "not_used", "not_used", "all_satellite_channels_available", "useful_satellite_channels_missing", "mandatory_satellite_channels_missing", "all_NWP_fields_available", "useful_NWP_fields_missing", "mandatory_NWP_fields_missing", "all_product_data_available", "useful_product_data_missing", "mandatory_product_data_missing", "all_auxiliary_data_available", "useful_auxiliary_data_missing", "mandatory_auxiliary_data_missing"]

flag_values_quality = [1, 2, 4, 8, 16, 24, 32]
flag_meanings_quality = ["nodata", "internal_consistency", "temporal_consistency", "good", "questionable", "bad", "interpolated"]

#plot_ci_flag_distribution(ds_combined['ci_status_flag'].values.flatten(), flag_values, flag_meanings, 'ci_status_flag', fig_folder)
#plot_ci_flag_distribution(ds_combined['ci_conditions'].values.flatten(), flag_values_conditions, flag_meanings_conditions, 'ci_conditions', fig_folder)
plot_ci_flag_distribution(ds_combined['ci_quality'].values.flatten(), flag_values_quality, flag_meanings_quality, 'ci_quality', fig_folder)

