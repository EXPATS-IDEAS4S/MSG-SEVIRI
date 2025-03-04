import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

output_folder = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/quality_flags_fig/'

# Open csv file of the closed points
df = pd.read_csv(f'{output_folder}cloud_mask_closed_points_flags.csv')

# Select only rows with structure 3x3
df = df[df['structure'] == '3x3']

print(df)

# Group by 'time' and count the number of rows for each time
result_df = df.groupby('time').size().reset_index(name='count')

# Display the resulting dataframe
print(result_df)

# Define the time range
start_time = "2013-04-01 00:00:00"
end_time = "2013-09-30 23:45:00"
time_range = pd.date_range(start=start_time, end=end_time, freq='15T')
tot_crops = len(time_range)
tot_points = tot_crops * 128 * 128

# Ensure the 'time' column is in datetime format
result_df['time'] = pd.to_datetime(result_df['time'])

# Create a dataframe with the full time range
full_time_df = pd.DataFrame({'time': time_range})

# Merge the original result_df with the full time range
complete_df = pd.merge(full_time_df, result_df, on='time', how='left')

# Fill missing counts with 0
complete_df['count'] = complete_df['count'].fillna(0).astype(int)

# Display the resulting dataframe
print(complete_df)


# Define thresholds
thresholds = [100, 500, 1000]


# Plot the distribution of the counts
plt.figure(figsize=(7, 3))

# Define the normalization term (e.g., tot_crops or any other value)
normalization_factor = tot_crops  # Replace with your desired term for normalization

# Histogram parameters
bin_min = 0
bin_max = 3000
bin_width = 100
bins = np.arange(bin_min, bin_max, bin_width)

# Calculate histogram values manually
hist_values, bin_edges = np.histogram(complete_df['count'], bins=bins)
normalized_values = hist_values / normalization_factor  # Manually normalize by the specified term

# Plot the normalized histogram
plt.bar(bin_edges[:-1], normalized_values, width=bin_width, color='skyblue', alpha=0.7, edgecolor='black')

# Add KDE manually for better control (optional)
#sns.kdeplot(complete_df['count'], color='blue', lw=2)

# Vertical lines for thresholds
for threshold in thresholds:
    plt.axvline(threshold, color='red', linestyle='--', lw=1)

# Customize the plot
plt.title('Normalized Distribution of Closed Holes', fontsize=16, fontweight='bold')
plt.xlabel('Closed Holes Count', fontsize=14)
plt.ylabel('Occurence ratio', fontsize=14)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# Save the plot
plt.savefig(f'{output_folder}manual_normalized_distribution.png', bbox_inches='tight')


# Calculate the number of rows exceeding each threshold
rows_above_threshold = {threshold: (complete_df['count'] > threshold).sum() for threshold in thresholds}

# Convert to DataFrame for easier plotting
thresholds_df = pd.DataFrame(list(rows_above_threshold.items()), columns=['Threshold', 'Rows'])


# Normalize the 'Rows' column manually
normalization_factor = thresholds_df['Rows'].sum()  # Replace with your desired term for normalization
thresholds_df['Normalized_Rows'] = thresholds_df['Rows'] / normalization_factor

# Print the normalized number of images for each threshold
for threshold, normalized_value in zip(thresholds_df['Threshold'], thresholds_df['Normalized_Rows']):
    print(f"Threshold: {threshold}, Normalized Number of Images: {normalized_value:.4f}")

# Threshold: 100, Normalized Number of Images: 0.6479
# Threshold: 500, Normalized Number of Images: 0.2911
# Threshold: 1000, Normalized Number of Images: 0.0610

# # Plot
# plt.figure(figsize=(4, 3))
# plt.bar(thresholds_df['Threshold'], thresholds_df['Normalized_Rows'], 
#         color='skyblue', edgecolor='black', width=0.6)

# # Customize the plot
# plt.title('Number of images above thresholds (Normalized)', fontsize=12, fontweight='bold')
# plt.xlabel('Threshold', fontsize=12)
# plt.ylabel('Normalized Number of Images', fontsize=12)
# plt.xticks(fontsize=12)
# plt.yticks(fontsize=12)
# # plt.grid(alpha=0.3)

# # Show and save the plot
# plt.savefig(f'{output_folder}normalized_counts_above_thresholds.png', bbox_inches='tight')




# # Sort the counts and calculate cumulative sum
# sorted_counts = np.sort(complete_df['count'])
# cumulative_counts = np.cumsum(sorted_counts)

# # Normalize the cumulative counts to make it relative
# normalized_cumulative_counts = cumulative_counts / cumulative_counts[-1]

# # Plot the cumulative distribution
# plt.figure(figsize=(10, 6))
# plt.plot(sorted_counts, normalized_cumulative_counts, color='blue', lw=2)

# # Customize the plot
# plt.title('Cumulative Distribution of Counts', fontsize=16, fontweight='bold')
# plt.xlabel('Counts', fontsize=14)
# plt.ylabel('Cumulative Probability', fontsize=14)
# plt.grid(alpha=0.3)
# plt.xticks(fontsize=12)
# plt.yticks(fontsize=12)

# # Show the plot
# plt.savefig(f'{output_folder}cumulative_of_counts.png', bbox_inches='tight')