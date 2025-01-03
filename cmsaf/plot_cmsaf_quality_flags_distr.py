import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from flags_category_names import quality_mapping, conditions_mapping, status_flag_mapping

output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"
# Open csv file as dataframe
df = pd.read_csv(f'{output_path}cloud_mask_closed_points_flags.csv')

df = df.apply(pd.to_numeric, errors='ignore', downcast='integer')

# # Convert data to pandas DataFrame for plotting
# df = pd.DataFrame({
#     'quality': pd.Series(df['quality']).map(quality_mapping).dropna(),
#     'conditions': pd.Series(df['conditions']).map(conditions_mapping).dropna(),
#     'status_flag': pd.Series(df['status_flag']).map(status_flag_mapping).dropna()
# })

#print number of roww with 3x3 structure
print(df['structure'].value_counts())
exit()


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
print(df[['status_flag', 'decoded_status_flag']])
print(df[['quality', 'decoded_quality']])
print(df[['conditions', 'decoded_conditions']])


# Split the decoded columns into individual items and count occurrences
from collections import Counter

def count_items(column):
    items = column.str.split(', ').explode()
    return Counter(items)

quality_counts = count_items(df['decoded_quality'])
conditions_counts = count_items(df['decoded_conditions'])
status_flag_counts = count_items(df['decoded_status_flag'])

# Convert counts to DataFrame for plotting
quality_df = pd.DataFrame(quality_counts.items(), columns=['quality', 'count'])
conditions_df = pd.DataFrame(conditions_counts.items(), columns=['conditions', 'count'])
status_flag_df = pd.DataFrame(status_flag_counts.items(), columns=['status_flag', 'count'])


for name, df in zip(['Quality', 'Conditions', 'Status_Flag'], [quality_df, conditions_df, status_flag_df]):
    # Plotting the counts
    fig, ax = plt.subplots(figsize=(12, 8))

    sns.barplot(data=df, x=name.lower(), y='count', ax=ax, color='skyblue')
    ax.set_title(f'Count of {name} Items', fontsize=14, fontweight='bold')
    ax.set_xlabel(name, fontsize=12)
    ax.set_ylabel('Count', fontsize=12)
    ax.yticks(fontsize=12)
    ax.tick_params(axis='x', rotation=45, labelsize=14)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')  # Align text with the end on the left
    plt.savefig(f'{output_path}cma_{name.lower()}_flags_items_count.png', bbox_inches='tight')

exit()


# Create subplots
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# Variables and their labels
#variables = ['quality', 'conditions', 'status_flag']
variables = ['decoded_quality', 'decoded_conditions', 'decoded_status_flag']
titles = ['Normalized Distribution of Quality', 
          'Normalized Distribution of Conditions', 
          'Normalized Distribution of Status Flag']

# Loop through each structure
for structure in df['structure'].unique():
    # Subset the DataFrame for the current structure
    structure_df = df[df['structure'] == structure]

    # Loop through each variable
    for var, title in zip(variables, titles):
        # Calculate normalized counts
        counts = structure_df[var].value_counts(normalize=True).reset_index()
        counts.columns = [var, 'normalized_count']

        # Create the plot
        plt.figure(figsize=(8, 6))
        sns.barplot(
            data=counts,
            x=var,
            y='normalized_count',
        )
        plt.title(f"{title} for Structure {structure}", fontsize=14, fontweight='bold')
        plt.xlabel("Categories", fontsize=12)
        plt.ylabel("Normalized Counts", fontsize=12)
        plt.xticks(rotation=45, ha="right", fontsize=12)
        plt.yticks(fontsize=12)

        # Save the figure
        plt.tight_layout()
        plt.savefig(f'{output_path}{structure}_cma_quality_flags_{var}.png', bbox_inches='tight')