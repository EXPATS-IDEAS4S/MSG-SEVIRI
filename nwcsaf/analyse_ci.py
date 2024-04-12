"""
This script performs several operations involving satellite data visualization and analysis. 
It is designed to handle cloud imaging data and uses machine learning frameworks to process 
and display the data in various formats.

Operations include:
- Appending a time attribute from metadata to the datasets.
- Combining multiple datasets into a single multi-time dataset using xarray.
- Opening and printing dataset details for orography.
- Setting up plotting parameters and generating visualizations for cloud probability data.
- Creating GIFs from a series of images.
- Analyzing and visualizing different types of flags and conditions in the cloud imaging data.

Key Variables:
- `ci_folder`: Directory containing cloud imaging (CI) files.
- `ci_filepattern`: Pattern matching the CI filenames.
- `fig_folder`: Directory to store output figures.
- `path_oro`: Path to the orography dataset.

Modules:
- `xarray` for data structure and operations.
- `pandas` for handling time conversions.
- `matplotlib` for creating visualizations.
- Custom modules from '/home/dcorradi/Documents/Codes/NIMROD/' for specific plot and quality check functions.

The script uses paths and variables specific to the author's environment, so adjustments may be necessary to match different deployment contexts.

@author: Daniele Corradini
"""

import xarray as xr
from glob import glob
import sys
import pandas as pd
import matplotlib.colors as mcolors
from matplotlib.patches import Patch

from plot_ci_functions import plot_ci, plot_ci_flag_distribution, compute_normalized_count, plot_ci_count

sys.path.append('/home/dcorradi/Documents/Codes/')
from NIMROD.figures.quality_check_functions import create_gif_from_folder


#Define paths and filepatter

#convective initiation nc files folder and filepattern
ci_folder = "/work/dcorradi/case_studies_expats/Hailstorm_July_2023/data/NWCSAF/CI/"
ci_filepattern = "S_NWC_CI_MSG3_EXPATS-VISIR_*.nc"
#path for saving figures
fig_folder = "/work/dcorradi/case_studies_expats/Hailstorm_July_2023/fig/CI/"
#path to orography
path_oro = "/net/ostro/figs_proposal_TEAMX/orography_expats_high_res.nc"

#list of all MSG data
fnames_ci = sorted(glob(ci_folder+ci_filepattern))
print('number of files found:', len(fnames_ci))

#function for adjusting time coordinates
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

#open orography
ds_oro = xr.open_dataset(path_oro)
print('orography\n',ds_oro)

# Defin Variable names
ci_probs_var=['ci_prob30', 'ci_prob60', 'ci_prob90']

#define domains of interest
domain_expats = [5. , 16. , 43. , 51.5]
domain_dfg  =  [10.75, 11.75,  45.5,  47.] # minlon, maxlon, minlat, maxlat

#set plotting par
#0: no probability; 1: 0-25% probability; 2: 25-50% probability; 3: 50-75% probability; 4: 75-100% probability

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
# Plot single maps
for file in fnames_ci:
    #open a single file
    ds = xr.open_dataset(file)
    lat=ds['lat'].values
    lon=ds['lon'].values
    time=ds.attrs['nominal_product_time']
    plot_ci(ds, lat, lon, time, ci_probs_var, domain_expats, cmap, norm, legend_labels,'expats', fig_folder)
    plot_ci(ds, lat, lon, time, ci_probs_var, domain_dfg, cmap, norm, legend_labels,'dfg', fig_folder)
"""

#create gif
#create_gif_from_folder(fig_folder+'maps/',fig_folder + 'CI_hailstorm2023.gif')

# flag_values = [0, 1, 2, 4, 8, 16, 32]
# flag_meanings = ['not_processed','High_resolution_satellite_data_used','Visible_data_used','IR3.9m_data_used','Cloud_type_data_used','Cloud_Microphysic_data_used','NWP_data_used']

# flag_values_conditions = [1, 2, 4, 6, 8, 16, 32, 48, 64, 128, 256, 512, 768, 1024, 2048, 3072, 4096, 8192, 12288, 16384, 32768, 49152]
# flag_meanings_conditions = ["space", "night", "day", "twilight", "sunglint", "land", "sea", "coast", "not_used", "not_used", "all_satellite_channels_available", "useful_satellite_channels_missing", "mandatory_satellite_channels_missing", "all_NWP_fields_available", "useful_NWP_fields_missing", "mandatory_NWP_fields_missing", "all_product_data_available", "useful_product_data_missing", "mandatory_product_data_missing", "all_auxiliary_data_available", "useful_auxiliary_data_missing", "mandatory_auxiliary_data_missing"]

# flag_values_quality = [1, 2, 4, 8, 16, 24, 32]
# flag_meanings_quality = ["nodata", "internal_consistency", "temporal_consistency", "good", "questionable", "bad", "interpolated"]

# plot_ci_flag_distribution(ds_combined['ci_status_flag'].values.flatten(), flag_values, flag_meanings, 'ci_status_flag', fig_folder)
# plot_ci_flag_distribution(ds_combined['ci_conditions'].values.flatten(), flag_values_conditions, flag_meanings_conditions, 'ci_conditions', fig_folder)
# plot_ci_flag_distribution(ds_combined['ci_quality'].values.flatten(), flag_values_quality, flag_meanings_quality, 'ci_quality', fig_folder)

count_ds = compute_normalized_count(ds_combined,ci_probs_var)
plot_ci_count(ds_oro, count_ds, ds_combined['lat'].values, ds_combined['lon'].values, ci_probs_var, domain_expats, 'YlOrRd', 'expats', fig_folder)
plot_ci_count(ds_oro, count_ds, ds_combined['lat'].values, ds_combined['lon'].values, ci_probs_var, domain_dfg, 'YlOrRd', 'dfg', fig_folder)
