import os
from glob import glob
import pandas as pd
from process_cma_functions import extract_data
from flags_category_names import quality_mapping, conditions_mapping, status_flag_mapping

# Define paths
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"

quality_df = pd.read_csv(os.path.join(output_path, "quality_flags_counts_2013_crops.csv"))
conditions_df = pd.read_csv(os.path.join(output_path, "conditions_flags_counts_2013_crops.csv"))
status_flag_df = pd.read_csv(os.path.join(output_path, "status_flags_counts_2013_crops.csv"))

#print(quality_df)
time_len = len(quality_df)
num_points_per_time = 128 * 128
tot_points = time_len * num_points_per_time
print("Quality Flags Rows:", len(quality_df))

# Flatten and count occurrences of each item in the 'decoded_flag' column
def count_items(df):
    # Split the 'decoded_flag' column into individual items, explode them into rows, and count occurrences
    df_exploded = df.assign(decoded_flag=df['decoded_flag'].str.split(', ')).explode('decoded_flag')
    total_counts = df_exploded.groupby('decoded_flag')['count'].sum().reset_index()
    total_counts.columns = ['item', 'tot_count']
    return total_counts

# Example usage
quality_totals = count_items(quality_df)
conditions_totals = count_items(conditions_df)
status_flag_totals = count_items(status_flag_df)

# Add columns with the normalized count using tot_points
quality_totals['norm_count'] = quality_totals['tot_count'] / tot_points
conditions_totals['norm_count'] = conditions_totals['tot_count'] / tot_points
status_flag_totals['norm_count'] = status_flag_totals['tot_count'] / tot_points

# Print results
print("Quality Flags Totals:")
print(quality_totals)

print("\nConditions Flags Totals:")
print(conditions_totals)

print("\nStatus Flags Totals:")
print(status_flag_totals)

# Save results to CSVs if needed
quality_totals.to_csv(os.path.join(output_path, "quality_flags_counts_per_items.csv"), index=False)
conditions_totals.to_csv(os.path.join(output_path, "conditions_flags_counts_per_items.csv"), index=False)
status_flag_totals.to_csv(os.path.join(output_path, "status_flags_counts_per_itmes.csv"), index=False)
