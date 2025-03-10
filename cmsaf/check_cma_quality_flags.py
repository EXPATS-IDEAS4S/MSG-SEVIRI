import os
from glob import glob
import pandas as pd
from process_cma_functions import extract_data
from flags_category_names import quality_mapping, conditions_mapping, status_flag_mapping

# Function to decode flags
def decode_flags_with_masks(value, flag_mapping):
    """
    Decode a flag value into its meaningful components considering both flag value and mask.
    """
    meanings = []
    for flag_value, details in flag_mapping.items():
        flag_mask = details["flag_mask"]
        #print(value, flag_mask, flag_value)
        # Check if the flag is active by applying the mask
        if (value & flag_mask) == flag_value:
            meanings.append(details["meaning"])
    return ', '.join(meanings)  # Combine all meanings into a single string


# Define paths
cma_crops_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/"
cma_product_path = "/data/sat/msg/CM_SAF/CMA_processed/"
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"

# Initialize DataFrames to store results
quality_df = pd.DataFrame()
conditions_df = pd.DataFrame()
status_flag_df = pd.DataFrame()

# Get all NetCDF files from cma_crops_path
nc_files = sorted(glob(os.path.join(cma_crops_path, "2013*.nc")))	
print(len(nc_files))

# Loop through files and accumulate flag counts
for nc_file in nc_files:
    # Extract data from file
    cma_ds = extract_data(nc_file, cma_product_path)
    print(cma_ds)
    exit()
    if cma_ds:
        # Extract timestamp
        timestamp = pd.to_datetime(cma_ds.time.values[0])  # Adjust if needed
        
        # Decode and count flag values
        for flag, mapping, df in [
            ("quality", quality_mapping, quality_df),
            ("conditions", conditions_mapping, conditions_df),
            ("status_flag", status_flag_mapping, status_flag_df),
        ]:
            if flag in cma_ds.variables:
                flag_values = cma_ds[flag].values.flatten()
                #Convert to integer
                flag_values = flag_values.astype(int)
                decoded_flags = [decode_flags_with_masks(value, mapping) for value in flag_values]
                flag_counts = pd.Series(decoded_flags).value_counts()
                
                # Append results to DataFrame
                temp_df = pd.DataFrame({
                    'time': [timestamp] * len(flag_counts),
                    'decoded_flag': flag_counts.index,
                    'count': flag_counts.values
                })
                if flag == "quality":
                    quality_df = pd.concat([quality_df, temp_df], ignore_index=True)
                elif flag == "conditions":
                    conditions_df = pd.concat([conditions_df, temp_df], ignore_index=True)
                elif flag == "status_flag":
                    status_flag_df = pd.concat([status_flag_df, temp_df], ignore_index=True)
        

# Save DataFrames to CSV files
quality_df.to_csv(os.path.join(output_path, "quality_flags_counts_2013_crops.csv"), index=False)
conditions_df.to_csv(os.path.join(output_path, "conditions_flags_counts_2013_crops.csv"), index=False)
status_flag_df.to_csv(os.path.join(output_path, "status_flags_counts_2013_crops.csv"), index=False)

#2509106 nohup





















# import os
# from glob import glob
# import matplotlib.pyplot as plt
# import pandas as pd
# import seaborn as sns

# from process_cma_functions import extract_data
# from flags_category_names import cma_mapping, quality_mapping, conditions_mapping, status_flag_mapping

# # Define paths
# cma_crops_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/"
# cma_product_path = "/data/sat/msg/CM_SAF/CMA_processed/"
# output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"

# # Initialize data collection
# data = {var: [] for var in ['quality', 'status_flag', 'conditions', 'cma']}

# # Get all NetCDF files from cma_crops_path
# nc_files = sorted(glob(os.path.join(cma_crops_path, "2013*.nc")))



# # Loop through files and accumulate data
# for nc_file in nc_files:
#     cma_ds = extract_data(nc_file, cma_product_path)
#     if cma_ds:
#         for var in data.keys():
#             if var in cma_ds.variables:
#                 data[var].extend(cma_ds[var].values.flatten())

# # Convert data to pandas DataFrame for plotting
# df = pd.DataFrame({
#     'quality': pd.Series(data['quality']).map(quality_mapping).dropna(),
#     'conditions': pd.Series(data['conditions']).map(conditions_mapping).dropna(),
#     'status_flag': pd.Series(data['status_flag']).map(status_flag_mapping).dropna(),
#     'cma': pd.Series(data['cma']).map(cma_mapping).dropna()
# })

# print(df)
# #save to csv
# df.to_csv(f'{output_path}cma_quality_flags.csv')
# exit()

# # Create subplots
# fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# # Variables and their labels
# variables = ['quality', 'conditions', 'status_flag', 'cma']
# titles = ['Normalized Distribution of Quality', 
#           'Normalized Distribution of Conditions', 
#           'Normalized Distribution of Status Flag', 
#           'Normalized Distribution of CMA']

# # Plot each variable
# for ax, var, title in zip(axes.flatten(), variables, titles):
#     # Calculate normalized counts
#     counts = df[var].value_counts(normalize=True)
#     print(counts)
#     if counts.empty:
#         continue
#     else:
#         fig, ax = plt.subplots(figsize=(8, 6))
#         sns.barplot(
#             x=counts.index, 
#             y=counts.values
#         )
#         plt.title(title, fontsize=14, fontweight='bold')
#         plt.xlabel("Categories", fontsize=12)
#         plt.ylabel("Normalized Counts",fontsize=12)
#         plt.xticks(rotation=45, ha="right",fontsize=12)
#         plt.yticks(fontsize=12)
#         fig.savefig(f'{output_path}cma_quality_flgs_{var}.png', bbox_inches='tight')

# #554359 nohup 