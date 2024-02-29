"""
Config file for the parameters needeed to process the MSG data
"""

#Path to the MSG files 
#path_to_file = "/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/MSG/HRSEVIRI_20220712_20210715_Flood_domain_DataTailor_nat/"
path_to_file = "/net/yube/case_studies_expats/Germany_Flood_2021/data/MSG/MSGNATIVE/"  

#Path tp the Clout Top Height files
path_to_cth = "/net/yube/case_studies_expats/Germany_Flood_2021/data/cloud_products/CTH_NWCSAF/NWC_SAF/" 

#filepattern of the MSG files
natfile = "MSG4-SEVI-MSG15-*-NA.subset.nat"


#filepattern of the CTH files
cth_file = "S_NWC_CTTH*.nc" #'CTXin*.nc'

#Domain
lonmin, latmin, lonmax, latmax= 5, 48, 9, 52 #2021 Germany Flood Area

#Define channel names
channels = ['IR_016', 'IR_039', 'IR_087', 'IR_097', 'IR_108', 'IR_120', 'IR_134', 'VIS006', 'VIS008', 'WV_062', 'WV_073']

# Flag to perform parallax correction
parallax_correction = True

# Flag for regular gridding
regular_grid = True
step_deg = 0.03 #correspond to around 3-4 km the actual resolution of MSG

#Satpy reader for MSG data and cth
msg_reader = 'seviri_l1b_native'
cth_reader = "nwcsaf-geo" #"cmsaf-claas2_l2_nc"