"""
Config file for the parameters needeed to process the MSG data
"""
# %%
#Path to the MSG files 
#path_to_file = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_Flood_domain_DataTailor_nat/"
#path_to_file = "/net/yube/case_studies_expats/Germany_Flood_2021/data/MSG/MSGNATIVE/" 
path_to_file = "/data/sat/msg/rapid_scan/nat/"

#Path tp the Clout Top Height files
#path_to_cth = "/net/yube/case_studies_expats/Germany_Flood_2021/data/cloud_products/CTH_NWCSAF/NWC_SAF/" 
path_to_cth = "/data/sat/msg/CM_SAF/CTH_processed/"

#filepattern of the MSG files
natfile = "MSG*-SEVI-MSG*-*-NA.subset.nat"

#filepattern of the CTH files
cth_file = 'CTXin*.nc' #"S_NWC_CTTH*.nc" 

#path to the folder to store processed netcdf
path_to_save = "/data/sat/msg/rapid_scan/netcdf/"

#Domain
#lonmin, latmin, lonmax, latmax= 5, 48, 9, 52 #2021 Germany Flood Area
lonmin, latmin, lonmax, latmax= 5, 42, 16, 51.5 #EXPATS

#Define channel names
channels = ['IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']
channels_unit = ['Reflectances (%)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Brightness Temperature (K)', 'Reflectances (%)', 'Reflectances (%)', 'Brightness Temperature (K)', 'Brightness Temperature (K)']
channels_cmaps = ['gray', 'cool', 'cool', 'cool', 'cool', 'cool', 'cool', 'gray', 'gray', 'cool', 'cool']

# Flag to perform parallax correction
parallax_correction = True

# Flag for regular gridding
regular_grid = True
step_deg = 0.04 #correspond to around 3-4 km the actual resolution of MSG
interp_method = 'nearest'

# MSG time resolution
msg_res = 5

# cth time resolution
cth_res = 15

#Satpy reader for MSG data and cth
msg_reader = 'seviri_l1b_native'
cth_reader = "cmsaf-claas3_l2_nc" #"nwcsaf-geo" 

# settings for study period
year = 2022
month = 9 #use "*" if all months considered

# %%
