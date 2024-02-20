"""
Filename, directories, 
"""
from glob import glob

# Define the file path where nat files are downloaded
path_to_file = "/data/sat/msg/test/" 

# define filename list of nat files for 
natfile = "*NA.subset.nat"
nat_fnames = sorted(glob(path_to_file+natfile))


# define NWC SAF product file folder (for convective index and cloud top height)
path_to_cth = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/" 

# define NWCSAF product filename list for 
cth_file = 'CTXin*.nc'
cth_fnames = sorted(glob(path_to_cth+cth_file))


# define folder where to store msg files converted to ncdf
path_ncdf = '/data/sat/msg/test/ncdf/'
filelist_ncdf = sorted(glob(path_ncdf+"*.nc"))

# file path for raster 
raster_filename = '/net/yube/ESSL/NE1_HR_LC_SR_W_DR/NE1_HR_LC_SR_W_DR.tif'

# file path for figures
path_figs = '/net/ostro/figs_proposal_TEAMX/'
