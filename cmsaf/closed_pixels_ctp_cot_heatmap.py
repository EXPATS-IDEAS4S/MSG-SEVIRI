import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Read the DataFrame from a CSV file
output_path = "/home/Daniele/fig/cma_analysis/closing_algorithm/"
csv_path = f'{output_path}cloud_mask_closed_points_cloud_properties.csv'  # Replace with your file path
df = pd.read_csv(csv_path)

# Specify the columns to use for the heatmap
x_col = 'ctp'  # Replace with the actual column name for the x-axis
y_col = 'cot'  # Replace with the actual column name for the y-axis

# Drop rows with NaN values in the selected columns
df = df[[x_col, y_col]].dropna()

# Create a pivot table counting the occurrences of each (x, y) pair
heatmap_data = df.groupby([x_col, y_col]).size().unstack(fill_value=0)

# Plot the heatmap
plt.figure(figsize=(6, 6))
ax = sns.heatmap(
    heatmap_data,
    cmap='viridis',  # Choose your preferred colormap
    cbar_kws={'label': 'Count'},  # Add a colorbar label
    mask=(heatmap_data == 0),  # Mask cells with zero count (will be blank)
    linewidths=0.5,  # Add grid lines between cells
    linecolor='white'
)

# Customize the axes
plt.xlabel(x_col, fontsize=12)
plt.ylabel(y_col, fontsize=12)
plt.title(f'2D Heatmap of {x_col} vs {y_col}', fontsize=14, fontweight='bold')

# Show the plot
plt.savefig(f'{output_path}heatmap_closed_pixels_cot_ctp.png', bbox_inches='tight')
