cma_mapping = {
    0: {"meaning": "clear_sky", "flag_mask": None},
    1: {"meaning": "cloudy", "flag_mask": None}
}

quality_mapping = {
    1: {"meaning": "no_data", "flag_mask": 1},
    2: {"meaning": "spare_bit", "flag_mask": 2},
    4: {"meaning": "spare_bit", "flag_mask": 4},
    8: {"meaning": "good", "flag_mask": 56},
    16: {"meaning": "questionable", "flag_mask": 56},
    24: {"meaning": "bad", "flag_mask": 56},
    32: {"meaning": "interpolated_reclassified", "flag_mask": 56}
}

conditions_mapping = {
    1: {"meaning": "outside_swath", "flag_mask": 1},
    2: {"meaning": "night", "flag_mask": 6},
    4: {"meaning": "day", "flag_mask": 6},
    6: {"meaning": "twilight", "flag_mask": 6},
    8: {"meaning": "sunglint", "flag_mask": 8},
    16: {"meaning": "land", "flag_mask": 48},
    32: {"meaning": "sea", "flag_mask": 48},
    48: {"meaning": "coast", "flag_mask": 48},
    64: {"meaning": "high_terrain", "flag_mask": 64},
    128: {"meaning": "rough_terrain", "flag_mask": 128},
    256: {"meaning": "all_satellite_channels_available", "flag_mask": 768},
    512: {"meaning": "useful_satellite_channels_missing", "flag_mask": 768},
    768: {"meaning": "mandatory_satellite_channels_missing", "flag_mask": 768},
    1024: {"meaning": "all_NWP_fields_available", "flag_mask": 3072},
    2048: {"meaning": "useful_NWP_fields_missing", "flag_mask": 3072},
    3072: {"meaning": "mandatory_NWP_fields_missing", "flag_mask": 3072},
    4096: {"meaning": "all_product_data_available", "flag_mask": 12288},
    8192: {"meaning": "useful_product_data_missing", "flag_mask": 12288},
    12288: {"meaning": "mandatory_product_data_missing", "flag_mask": 12288},
    16384: {"meaning": "all_auxiliary_data_available", "flag_mask": 49152},
    32768: {"meaning": "useful_auxiliary_data_missing", "flag_mask": 49152},
    49152: {"meaning": "mandatory_auxiliary_data_missing", "flag_mask": 49152}
}

status_flag_mapping = {
    1: {"meaning": "ocean_marginal_seaice", "flag_mask": 31},
    2: {"meaning": "ocean_seaice", "flag_mask": 31},
    3: {"meaning": "ocean_icefree_north_vhi_lat", "flag_mask": 31},
    4: {"meaning": "ocean_icefree_north_hi_lat", "flag_mask": 31},
    5: {"meaning": "ocean_icefree_north_mid_lat_nosunglint", "flag_mask": 31},
    6: {"meaning": "ocean_icefree_tropical_nosunglint", "flag_mask": 31},
    7: {"meaning": "ocean_icefree_south_mid_lat_nosunglint", "flag_mask": 31},
    8: {"meaning": "ocean_icefree_south_hi_lat", "flag_mask": 31},
    9: {"meaning": "ocean_icefree_south_vhi_lat", "flag_mask": 31},
    10: {"meaning": "homogeneous_land_dry_snowfree", "flag_mask": 31},
    11: {"meaning": "homogeneous_land_extratropical_snowfree", "flag_mask": 31},
    12: {"meaning": "homogeneous_land_extratropical_snowcovered_seasonal", "flag_mask": 31},
    13: {"meaning": "homogeneous_land_extratropical_snowcovered_permanent", "flag_mask": 31},
    14: {"meaning": "rough_land_dry_snowfree", "flag_mask": 31},
    15: {"meaning": "rough_land_extratropical_snowfree", "flag_mask": 31},
    16: {"meaning": "rough_land_extratropical_snowcovered_seasonal", "flag_mask": 31},
    17: {"meaning": "rough_land_extratropical_snowcovered_permanent", "flag_mask": 31},
    18: {"meaning": "homogeneous_land_tropical_nondry", "flag_mask": 31},
    19: {"meaning": "rough_land_tropical_nondry", "flag_mask": 31},
    32: {"meaning": "Low_level_thermal_inversion_in_NWP_field", "flag_mask": 32},
    64: {"meaning": "Sea_ice_according_to_aux_data", "flag_mask": 64},
    128: {"meaning": "Snow_or_ice_according_to_NWCSAFPPS_CloudMask", "flag_mask": 128}
}



# ### **How the Decoding Works?**
# Each flag definition has two parts:
# 1. **Flag Value**: This is the specific configuration of switches for the flag.
# 2. **Flag Mask**: This tells you which switches are relevant for this flag.

# When decoding:
# 1. Use the mask to isolate only the relevant switches.
# 2. Check if the resulting value matches the flag value.

# **Example**:
# Let’s decode a value `129` with this mapping:
# - Flag 1: Value `1`, Mask `31` (binary `00011111`).
# - Flag 2: Value `2`, Mask `31`.
# - Flag 128: Value `128`, Mask `128` (binary `10000000`).

# **Steps**:
# 1. **Flag 1**:
#  - `(129 & 31) = 1` → Matches flag value `1`. So, **Flag 1 is active**.
# 2. **Flag 2**:
#  - `(129 & 31) = 1` → Does NOT match flag value `2`. So, **Flag 2 is not active**.
# 3. **Flag 128**:
#  - `(129 & 128) = 128` → Matches flag value `128`. So, **Flag 128 is active**.

# Final result: Flags 1 and 128 are active.


# ### **Why Do It This Way?**
# 1. **Efficiency**: Bitwise operations are very fast, so it’s easy to store and process multiple flags in a single number.
# 2. **Compactness**: Instead of storing lots of separate "yes/no" values, you pack everything into one number.
# 3. **Flexibility**: Masks let you focus on specific bits or flags, even if multiple flags are combined.

