import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import cmcrameri.cm as cmc

# Define the folder containing the CSV files
input_folder = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/cloud_property_flag"
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/"

# Collect all CSV files in the folder
csv_files = sorted([os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.endswith('.csv')])
print(f"Found {len(csv_files)} CSV files.")

# Take only the first 10 files for testing
#csv_files = csv_files 

# Read and concatenate all CSV files into a single DataFrame
df_list = [pd.read_csv(csv_file) for csv_file in csv_files]
df = pd.concat(df_list, axis=0, ignore_index=True)

# Specify the columns to use for the plots
x_col = 'ctp_regridded'  # Replace with the actual column name for the x-axis
y_col = 'cot_regridded'  # Replace with the actual column name for the y-axis

# Drop rows with NaN values in the selected columns
df = df[[x_col, y_col]].dropna()

# Print the min and max of the selected columns
print(f"Min {x_col}: {df[x_col].min()}, Max {x_col}: {df[x_col].max()}")
print(f"Min {y_col}: {df[y_col].min()}, Max {y_col}: {df[y_col].max()}")

# Take a random subset of the data for faster plotting
#df = df.sample(n=100000, random_state=42)

# Define bin settings
x_min, x_max, x_bin_width = 100, 1000, 25  # Example: bins from 0 to 1000 with width of 50
y_min, y_max, y_bin_width = 0.01, 10, 0.2    # Example: bins from 0 to 100 with width of 5

# Create bins for x and y
x_bins = np.arange(x_min, x_max + x_bin_width, x_bin_width)
y_bins = np.arange(y_min, y_max + y_bin_width, y_bin_width)


# Digitize x and y into bins
df['ctp_bin'] = pd.cut(df[x_col], bins=x_bins, labels=False, include_lowest=True)
df['cot_bin'] = pd.cut(df[y_col], bins=y_bins, labels=False, include_lowest=True)

# Create a pivot table counting occurrences for each (CTP, COT) pair
heatmap_data = (
    df.groupby(['ctp_bin', 'cot_bin'])
    .size()
    .unstack(fill_value=0)
)

# Normalize the heatmap counts to show proportions
heatmap_data_normalized = heatmap_data / heatmap_data.values.sum()

# Plot the heatmap
plt.figure(figsize=(6, 5))
ax = sns.heatmap(
    heatmap_data_normalized.T,  # Transpose to ensure CTP on x and COT on y
    cmap=cmc.lapaz,  # Colormap
    cbar_kws={'label': 'Normalized Count'},  # Label for the colorbar
    mask=(heatmap_data_normalized.T == 0),  # Mask zero counts to be white
    xticklabels=False,  # Disable x-axis labels
    yticklabels=False,  # Disable y-axis labels
    linewidths=0,  # Remove gridlines
    linecolor=None,  # No gridline color
    rasterized=True  # Improve rendering for smoother heatmaps
)

#the grid
#ax.grid(color='gray', linestyle='-', linewidth=0.5, alpha=0.5)

# Reverse the y-axis (place 0 at the bottom)
ax.invert_yaxis()

# Set ticks for x-axis to include only half of the bins
x_tick_indices = range(0, len(x_bins) - 1, 2)  # Select every second bin for ticks
ax.set_xticks(x_tick_indices)  # Set tick positions
ax.set_xticklabels([f"{int(x_bins[i])}" for i in x_tick_indices], rotation=45, fontsize=12)  # Set corresponding labels

# Set ticks for y-axis to include only half of the bins
y_tick_indices = range(0, len(y_bins) - 1, 2)  # Select every second bin for ticks
ax.set_yticks(y_tick_indices)  # Set tick positions
ax.set_yticklabels([f"{y_bins[i]:.1f}" for i in y_tick_indices], rotation=0, fontsize=12)  # Set corresponding labels

# Customize the labels and title
plt.xlabel("CTP (hPa)", fontsize=12)
plt.ylabel("COT", fontsize=12)
plt.title(f'2D Heatmap of CTP vs COT', fontsize=14, fontweight='bold')

# Save the heatmap plot
heatmap_output_path = os.path.join(output_path, 'heatmap_closed_pixels_cot_ctp.png')
plt.savefig(heatmap_output_path, bbox_inches='tight')
print(f"Heatmap saved to: {heatmap_output_path}")

exit()
### 2. Plot the scatterplot
plt.figure(figsize=(8, 6))
sns.scatterplot(data=df, x=x_col, y=y_col, alpha=0.5)

# Customize the scatterplot
plt.xlabel(x_col, fontsize=12)
plt.ylabel(y_col, fontsize=12)
#plt.yscale('log')  # Use a logarithmic scale for the y-axis
#plt.xscale('log')  # Use a logarithmic scale for the x-axis
plt.title(f'Scatterplot of {x_col} vs {y_col}', fontsize=14, fontweight='bold')

# Save the scatterplot
scatter_output_path = os.path.join(output_path, 'scatterplot_closed_pixels_cot_ctp.png')
plt.savefig(scatter_output_path, bbox_inches='tight')
print(f"Scatterplot saved to: {scatter_output_path}")


