"""
Filename, directories, 
"""
from glob import glob

# Define the file path where nat files are downloaded
path_to_file = "/data/sat/msg/test/" 

# path for dir tree ncdf files
path_dir_tree = "/data/sat/msg/"

# define filename list of nat files for 
nat_fnames = sorted(glob(path_to_file+"*NA.subset.nat"))


# define NWC SAF product file folder (for convective index and cloud top height)
path_to_cth = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/" 

# define NWCSAF product filename list for 
cth_file = 'CTXin*.nc'
cth_fnames = sorted(glob(path_to_cth+cth_file))


# define folder where to store msg files converted to ncdf
path_ncdf = '/data/sat/msg/test/ncdf/'
filelist_ncdf = sorted(glob(path_ncdf+"MSG*.nc"))

# file path for raster 
raster_filename = '/net/yube/ESSL/NE1_HR_LC_SR_W_DR/NE1_HR_LC_SR_W_DR.tif'

# file path for figures
path_figs = '/net/ostro/figs_proposal_TEAMX/'


# file containing orography for expats domain
orography_file = '/net/ostro/figs_proposal_TEAMX/orography_expats_high_res.nc'


# file path for raster 
raster_filename_1 = '/net/ostro/50N000E_20101117_gmted_max075.tif'
raster_filename_2 = '/net/ostro/30N000E_20101117_gmted_max075.tif'