import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

output_path = "/home/Daniele/fig/cma_analysis/modis/"

# Upload the csv file
results_df = pd.read_csv(f"{output_path}modis_cma_comparison.csv")

# List of structures used for binary closing
closing_structures = ['2x2', '3x3', '4x4', '5x5', '6x6', '7x7', '8x8', '9x9', '10x10']

#print the columns name of the dataframe
print(results_df['Condition'].value_counts())
exit()

# Plot the barplot showing the count of each condition for the closing structures
fig, ax = plt.subplots(figsize=(8, 5))
sns.countplot(data=results_df, x="Condition", order=closing_structures)
plt.title("Count of Each Condition for Closing Structures", fontsize=14, fontweight="bold")
plt.xlabel("Closing Algorithm Structure", fontsize=14)
plt.ylabel("Count", fontsize=14)
fig.savefig(f"{output_path}closed_points_all_structures.png", dpi=300, bbox_inches="tight")
