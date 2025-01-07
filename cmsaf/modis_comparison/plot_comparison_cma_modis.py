import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

output_path = "/home/Daniele/fig/cma_analysis/modis/"

# Upload the csv file
results_df = pd.read_csv(f"{output_path}modis_cma_comparison.csv")

# List of structures used for binary closing
closing_structures = ['2x2', '3x3', '4x4', '5x5', '6x6', '7x7', '8x8', '9x9', '10x10']

modis_labels = {0: "Cloudy", 1: "Probably Cloudy", 2: "Probably Clear", 3: "Confident Clear"}

# Plot the barplot of normalized counts for all structures together
results_df["MODIS Value"] = results_df["MODIS Value"].map(modis_labels)
normalized_counts = results_df.groupby(["MODIS Value", "Condition"]).size().reset_index(name='Count')
print(normalized_counts)
# Calculate total counts for each structure type
total_counts = normalized_counts.groupby("Condition")["Count"].sum().reset_index(name='Total Count')
print(total_counts)

# Merge total counts back into the results_df
normalized_counts = normalized_counts.merge(total_counts, on="Condition", how="left")

# Calculate normalized counts
normalized_counts["Normalized Count"] = normalized_counts["Count"] / normalized_counts["Total Count"]
print(normalized_counts)

fig, ax = plt.subplots(figsize=(12, 7))

# Define the desired order of the MODIS values in the legend
modis_order = ["Cloudy", "Probably Cloudy", "Probably Clear", "Confident Clear"]

# Plot the barplot with the correct order for the legend
sns.barplot(data=normalized_counts, x="Condition", y="Normalized Count", hue="MODIS Value", order=closing_structures, hue_order=modis_order)
plt.title(f"MODIS Cloud Mask Values in CMSAF Holes", fontsize=14, fontweight="bold")
plt.xlabel("Closing Algorithm Structure", fontsize=14)
plt.ylabel("Normalized Count", fontsize=14)

# put legend on the right side of the plot, outside the plot
plt.legend(title="MODIS values", fontsize=12, loc='center left', bbox_to_anchor=(1, 0.5))
# Place the ticks in order
plt.xticks(ticks=np.arange(len(closing_structures)), labels=closing_structures, fontsize=14, fontweight="bold")
plt.yticks(fontsize=14)
fig.savefig(f"{output_path}modis_cma_comparison_structure_all_structures.png", dpi=300, bbox_inches="tight")



# Create a new mapping for the merged categories
merged_labels = {
    "Cloudy": "Cloudy/Probably Cloudy",
    "Probably Cloudy": "Cloudy/Probably Cloudy",
    "Probably Clear": "Clear/Probably Clear",
    "Confident Clear": "Clear/Probably Clear"
}

# Update the DataFrame with the new labels
normalized_counts["Merged MODIS Value"] = normalized_counts["MODIS Value"].map(merged_labels)
print(normalized_counts)

# Calculate total counts for each merged category
merged_counts = normalized_counts.groupby(["Merged MODIS Value", "Condition"]).agg({'Count': 'sum'}).reset_index()
total_counts = merged_counts.groupby("Condition")["Count"].sum().reset_index(name='Total Count')

# Merge total counts back into the merged_counts
merged_counts = merged_counts.merge(total_counts, on="Condition", how="left")

# Calculate normalized counts
merged_counts["Normalized Count"] = merged_counts["Count"] / merged_counts["Total Count"]
print(merged_counts)

fig, ax = plt.subplots(figsize=(8, 5))

# Define the desired order of the merged MODIS values in the legend
merged_modis_order = ["Cloudy/Probably Cloudy", "Clear/Probably Clear"]

# Plot the barplot with the correct order for the legend
sns.barplot(data=merged_counts, x="Condition", y="Normalized Count", hue="Merged MODIS Value", order=closing_structures, hue_order=merged_modis_order)
plt.title(f"MODIS Cloud Mask Values in CMSAF Holes", fontsize=14, fontweight="bold")
plt.xlabel("Closing Algorithm Structure", fontsize=14)
plt.ylabel("Normalized Count", fontsize=14)
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

# Put legend on the right side of the plot, outside the plot
plt.legend(title="MODIS values", fontsize=12, loc='center left', bbox_to_anchor=(1, 0.5))
fig.savefig(f"{output_path}modis_cma_comparison_structure_merged.png", dpi=300, bbox_inches="tight")



exit()


# Loop over the structures
for structure in closing_structures:
    print(structure)
    # Filter the dataframe by the structure
    structure_df = results_df[results_df["Condition"] == structure]
    
    # Replace MODIS values with labels
    structure_df["MODIS Value"] = structure_df["MODIS Value"].map(modis_labels)
    print(structure_df)
    # Calculate normalized counts
    normalized_counts = structure_df.groupby(["MODIS Value"]).size().reset_index(name='Count')
    normalized_counts['Normalized Count'] = normalized_counts['Count'] / len(structure_df)

    print(normalized_counts)

    # Plot distribution
    fig, ax = plt.subplots(figsize=(6, 4))
    #plot the count nomralized by the total count

    #sns.countplot(data=structure_df, x="MODIS Value", hue="Condition")
    sns.barplot(data=normalized_counts, x="MODIS Value", y="Normalized Count")
    plt.title(f"MODIS Cloud Mask Values in CMSAF Holes {structure}", fontsize=14, fontweight="bold")
    plt.xlabel("MODIS Cloud Mask Value", fontsize=14)
    plt.ylabel("Normalized Count", fontsize=14)
    #plt.legend(title="Condition", fontsize=12)
    # Place the ticks in order
    plt.xticks(ticks=np.arange(4), labels=list(modis_labels.values()), fontsize=14, fontweight="bold")
    plt.yticks(fontsize=14)
    fig.savefig(f"{output_path}modis_cma_comparison_structure_{structure}.png", dpi=300, bbox_inches="tight")
    