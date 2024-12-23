# Category mappings for better labels
cma_mapping = {
    0: "clear_sky", 1: "cloudy"
}

quality_mapping = {
    1: "no_data", 2: "spare_bit", 4: "spare_bit", 8: "good", 16: "questionable", 
    24: "bad", 32: "interpolated_reclassified"
}
conditions_mapping = {
    1: "outside_swath", 2: "night", 4: "day", 6: "twilight", 8: "sunglint", 16: "land", 
    32: "sea", 48: "coast", 64: "high_terrain", 128: "rough_terrain", 256: "all_satellite_channels_available",
    512: "useful_satellite_channels_missing", 768: "mandatory_satellite_channels_missing",
    1024: "all_NWP_fields_available", 2048: "useful_NWP_fields_missing",
    3072: "mandatory_NWP_fields_missing", 4096: "all_product_data_available",
    8192: "useful_product_data_missing", 12288: "mandatory_product_data_missing",
    16384: "all_auxiliary_data_available", 32768: "useful_auxiliary_data_missing",
    49152: "mandatory_auxiliary_data_missing"
}
status_flag_mapping = {
    1: "ocean_marginal_seaice", 2: "ocean_seaice", 3: "ocean_icefree_north_vhi_lat", 
    4: "ocean_icefree_north_hi_lat", 5: "ocean_icefree_north_mid_lat_nosunglint", 
    6: "ocean_icefree_tropical_nosunglint", 7: "ocean_icefree_south_mid_lat_nosunglint", 
    8: "ocean_icefree_south_hi_lat", 9: "ocean_icefree_south_vhi_lat", 10: "homogeneous_land_dry_snowfree",
    # Add other mappings here as necessary
}