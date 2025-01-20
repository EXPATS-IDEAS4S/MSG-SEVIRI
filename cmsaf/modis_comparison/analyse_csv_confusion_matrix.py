import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Path to the output directory
output_path = "/home/Daniele/fig/cma_analysis/modis/conf_matrix/closing/"

# Open the CSV file
results_df = pd.read_csv(f"{output_path}confusion_matrix_results_closing.csv")
print(results_df['Closing Structure'].unique())

# Remove all rows with Closing Structure higher then 5
results_df = results_df[results_df['Closing Structure'] <= 5]

# Normalize False Negatives (FN) by the total count (TN + FP + FN + TP) in each row
results_df['Total Count'] = results_df['True Negatives'] + results_df['False Positives'] + results_df['False Negatives'] + results_df['True Positives']
results_df['Normalized FN'] = results_df['False Negatives'] / results_df['Total Count']
results_df['Normalized FN'] = results_df['Normalized FN'].round(2)
results_df['Normalized FP'] = results_df['False Positives'] / results_df['Total Count']
results_df['Normalized FP'] = results_df['Normalized FP'].round(2)

# Check the DataFrame columns
print(results_df.columns)

# Create a boxplot with seaborn (no outliers)
plt.figure(figsize=(10, 6))
sns.boxplot(data=results_df, x='Closing Structure', y='Normalized FP', color='skyblue', showfliers=False)   

# Add title and labels
plt.title('Distribution of Normalized False Positive (FP) Across Closing Structures', fontsize=14, fontweight='bold')
plt.xlabel('Closing Structure', fontsize=12)
plt.ylabel('Normalized False Positive (FP)', fontsize=12)

# Adjust layout and show the plot
plt.savefig(f"{output_path}normalized_fp_boxplot.png", dpi=300, bbox_inches='tight')


# Create a boxplot with seaborn (no outliers)
plt.figure(figsize=(10, 6))
sns.boxplot(data=results_df, x='Closing Structure', y='Normalized FN', color='skyblue', showfliers=False)   

# Add title and labels
plt.title('Distribution of Normalized False Negative (FN) Across Closing Structures', fontsize=14, fontweight='bold')
plt.xlabel('Closing Structure', fontsize=12)
plt.ylabel('Normalized False Negative (FN)', fontsize=12)

# Adjust layout and show the plot
plt.savefig(f"{output_path}normalized_fn_boxplot.png", dpi=300, bbox_inches='tight')

# Compute ets score
# First compute the  hits expected by chance) like
#a r = (total forecasts of the event) * (total observations of the event) / (sample size)
results_df['Random Hits'] = (results_df['True Positives'] + results_df['False Positives']) * (results_df['True Positives'] + results_df['False Negatives']) / results_df['Total Count']

results_df['ETS'] = (results_df['True Positives'] - results_df['Random Hits']) / (results_df['True Positives'] + results_df['False Positives'] + results_df['False Negatives'] - results_df['Random Hits'])

# Create a boxplot with seaborn (no outliers) for the ETS score

plt.figure(figsize=(6, 4))
sns.boxplot(data=results_df, x='Closing Structure', y='ETS', color='skyblue', showfliers=False)   

# Add title and labels
plt.title('Distribution of ETS Across Closing Structures', fontsize=12, fontweight='bold')
plt.xlabel('Closing Structure', fontsize=12)
plt.ylabel('ETS', fontsize=12)

# Adjust layout and show the plot
plt.savefig(f"{output_path}ets_boxplot.png", dpi=300, bbox_inches='tight')
