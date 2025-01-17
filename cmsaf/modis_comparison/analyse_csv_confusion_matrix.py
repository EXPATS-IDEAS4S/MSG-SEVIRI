import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Path to the output directory
output_path = "/home/Daniele/fig/cma_analysis/modis/conf_matrix/closing/"

# Open the CSV file
results_df = pd.read_csv(f"{output_path}confusion_matrix_results_closing.csv")

# Normalize False Negatives (FN) by the total count (TN + FP + FN + TP) in each row
results_df['Total Count'] = results_df['True Negatives'] + results_df['False Positives'] + results_df['False Negatives'] + results_df['True Positives']
results_df['Normalized FN'] = results_df['False Negatives'] / results_df['Total Count']

# Check the DataFrame structure to ensure correctness
print(results_df.head())

# Create a boxplot with seaborn
plt.figure(figsize=(10, 6))
sns.boxplot(data=results_df, x='Closing Structure', y='Normalized FN', color='skyblue')

# Add title and labels
plt.title('Distribution of Normalized False Negatives (FN) Across Closing Structures', fontsize=14, fontweight='bold')
plt.xlabel('Closing Structure', fontsize=12)
plt.ylabel('Normalized False Negatives (FN)', fontsize=12)

# Adjust layout and show the plot
plt.savefig(f"{output_path}normalized_fn_boxplot.png", dpi=300, bbox_inches='tight')

