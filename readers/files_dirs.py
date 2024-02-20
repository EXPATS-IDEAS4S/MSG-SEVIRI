"""
Filename, directories, 
"""
from glob import glob


path_ncdf = '/data/sat/msg/test/ncdf/'
filelist_ncdf = sorted(glob(path_ncdf+"*.nc"))

raster_filename = '/net/yube/ESSL/NE1_HR_LC_SR_W_DR/NE1_HR_LC_SR_W_DR.tif'
path_figs = '/net/ostro/figs_proposal_TEAMX/'
