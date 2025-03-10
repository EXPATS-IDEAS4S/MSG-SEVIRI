import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import os

from flags_category_names import quality_mapping, conditions_mapping, status_flag_mapping

output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"

# Open csv file as dataframe
df = pd.read_csv(f'{output_path}cloud_mask_closed_points_flags.csv')

df = df.apply(pd.to_numeric, errors='ignore', downcast='integer')
#print(df['structure'].value_counts())
#select only rows with structure 3x3
df = df[df['structure'] == '3x3']
tot_rows = len(df)
print(tot_rows)
print(df)

# # Convert data to pandas DataFrame for plotting
# df = pd.DataFrame({
#     'quality': pd.Series(df['quality']).map(quality_mapping).dropna(),
#     'conditions': pd.Series(df['conditions']).map(conditions_mapping).dropna(),
#     'status_flag': pd.Series(df['status_flag']).map(status_flag_mapping).dropna()
# })

def decode_flags_with_masks(value, flag_mapping):
    """
    Decode a flag value into its meaningful components considering both flag value and mask.
    """
    meanings = []
    for flag_value, details in flag_mapping.items():
        flag_mask = details["flag_mask"]
        # Check if the flag is active by applying the mask
        if (value & flag_mask) == flag_value:
            meanings.append(details["meaning"])
    return ', '.join(meanings)  # Combine all meanings into a single string



# Decode the status_flag column using the updated function
df['decoded_status_flag'] = df['status_flag'].apply(lambda x: decode_flags_with_masks(x, status_flag_mapping))
df['decoded_quality'] = df['quality'].apply(lambda x: decode_flags_with_masks(x, quality_mapping))
df['decoded_conditions'] = df['conditions'].apply(lambda x: decode_flags_with_masks(x, conditions_mapping))

# Print the updated DataFrame for verification
#print(df[['status_flag', 'decoded_status_flag']])
#print(df[['quality', 'decoded_quality']])
#print(df[['conditions', 'decoded_conditions']])

# Plot how many rows have empty status_flag
print(df['decoded_status_flag'].value_counts())

# Split the decoded columns into individual items and count occurrences
from collections import Counter

def count_items(column):
    items = column.str.split(', ').explode()
    return Counter(items)

quality_counts = count_items(df['decoded_quality'])
conditions_counts = count_items(df['decoded_conditions'])
status_flag_counts = count_items(df['decoded_status_flag'])
#print(quality_counts)
#print(conditions_counts)
#print(status_flag_counts)

# Convert counts to DataFrame for plotting
quality_df = pd.DataFrame(quality_counts.items(), columns=['item', 'count'])
conditions_df = pd.DataFrame(conditions_counts.items(), columns=['item', 'count'])
status_flag_df = pd.DataFrame(status_flag_counts.items(), columns=['item', 'count'])

# Normalize by tot_rows
quality_df['normalized_count'] = quality_df['count'] / tot_rows
conditions_df['normalized_count'] = conditions_df['count'] / tot_rows
status_flag_df['normalized_count'] = status_flag_df['count'] / tot_rows

# Add a column called closed_pixeles and set all values to True
quality_df['closed_pixels'] = 'Yes'
conditions_df['closed_pixels'] = 'Yes'
status_flag_df['closed_pixels'] = 'Yes'

#print(quality_df)
#print(conditions_df)
#print(status_flag_df)

# Check the quality flags distribution for all points
quality_totals = pd.read_csv(os.path.join(output_path, "quality_flags_counts_per_items.csv"))
conditions_totals = pd.read_csv(os.path.join(output_path, "conditions_flags_counts_per_items.csv"))
status_flag_totals = pd.read_csv(os.path.join(output_path, "status_flags_counts_per_itmes.csv"))

# change columns name from tot_count to count and norm_count to normalized_count
quality_totals.columns = ['item', 'count', 'normalized_count']
conditions_totals.columns = ['item', 'count', 'normalized_count']
status_flag_totals.columns = ['item', 'count', 'normalized_count']

# Add a column called closed_pixeles and set all values to False
quality_totals['closed_pixels'] = 'No'
conditions_totals['closed_pixels'] = 'No'
status_flag_totals['closed_pixels'] = 'No'

#print(quality_totals)
#print(conditions_totals)
#print(status_flag_totals)

# Concatenate the two DataFrames
quality_df = pd.concat([quality_df, quality_totals], ignore_index=True)
conditions_df = pd.concat([conditions_df, conditions_totals], ignore_index=True)
status_flag_df = pd.concat([status_flag_df, status_flag_totals], ignore_index=True)
print(quality_df)
print(conditions_df)
print(status_flag_df)

# if dataframs have item column with no value (empty), rename it as 'uncategorized'
quality_df['item'] = quality_df['item'].replace('', 'uncategorized')
conditions_df['item'] = conditions_df['item'].replace('', 'uncategorized')
status_flag_df['item'] = status_flag_df['item'].replace('', 'uncategorized')

# #print the list of columns item
# print(quality_df['item'].unique())
# print(conditions_df['item'].unique())
# print(status_flag_df['item'].unique())


conditions_items_list = ['all_satellite_channels_available', 'all_NWP_fields_available', 'all_auxiliary_data_available',
                         'mandatory_NWP_fields_missing',
                         'day', 'night', 'twilight', 
                         'land', 'sea', 'coast', 
                         'rough_terrain', 'high_terrain']

status_flag_items_list = ['rough_land_extratropical_snowfree',
                         'rough_land_extratropical_snowcovered_seasonal',
                         'rough_land_extratropical_snowcovered_permanent',
                         'rough_land_tropical_nondry',
                         'homogeneous_land_extratropical_snowcovered_seasonal',
                         'homogeneous_land_extratropical_snowcovered_permanent',
                         'homogeneous_land_extratropical_snowfree',
                         'homogeneous_land_tropical_nondry', 
                         'ocean_icefree_north_hi_lat', 
                         'ocean_icefree_north_mid_lat_nosunglint',
                         'ocean_icefree_tropical_nosunglint',
                         'Snow_or_ice_according_to_NWCSAFPPS_CloudMask',
                         'Low_level_thermal_inversion_in_NWP_field', 
                         'uncategorized']



# Adjust DataFrame item ordering
conditions_df['item'] = pd.Categorical(conditions_df['item'], categories=conditions_items_list, ordered=True)
conditions_df = conditions_df.sort_values('item')  # Ensure sorting based on the specified order
status_flag_df['item'] = pd.Categorical(status_flag_df['item'], categories=status_flag_items_list, ordered=True)
status_flag_df = status_flag_df.sort_values('item')  # Ensure sorting based on the specified order

# Iterate through DataFrames and create plots
for name, df in zip(['Quality', 'Conditions', 'Status_Flag'], [quality_df, conditions_df, status_flag_df]):
    # Sort only Conditions if applicable
    df = df.sort_values('item')

    # Plotting the counts
    fig, ax = plt.subplots(figsize=(3, 6))
    # Plot hue first yes and then no
    sns.barplot(data=df, x='normalized_count', y='item', hue='closed_pixels', hue_order=['Yes', 'No'], ax=ax)
    ax.set_title(f'Count of {name} Items', fontsize=12, fontweight='bold')
    ax.set_xlabel('Normalized Count', fontsize=12)
    ax.set_ylabel('', fontsize=12, fontweight='bold')

    # Set y-ticks explicitly for Conditions
    if name == 'Conditions':
        plt.yticks(range(len(conditions_items_list)), conditions_items_list, fontsize=12)
    elif name == 'Status_Flag':
        plt.yticks(range(len(status_flag_items_list)), status_flag_items_list, fontsize=12)
    else:
        plt.yticks(fontsize=12)

    # remove legend #
    ax.get_legend().remove()
    #plt.legend(title='Closed Pixels', fontsize=12)
    plt.savefig(f'{output_path}cma_{name.lower()}_flags_items_norm_count_closed_points.png', bbox_inches='tight')

