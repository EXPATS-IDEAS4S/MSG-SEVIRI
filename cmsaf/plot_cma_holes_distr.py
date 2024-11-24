from process_cma_functions import plot_normalized_histogram, plot_monthly_granular_distribution
from process_cma_functions import plot_normalized_histogram_from_csv, plot_temporal_granular_distribution_from_csv

# Define the output folder for the figures
output_folder = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/filling_cma_figs/'

# Get path of the csv file with the counts
monthly_counts_path = f'{output_folder}monthly_counts.csv'
aggregated_counts_path = f'{output_folder}aggregated_counts.csv'
total_points_by_category_path = f'{output_folder}total_points_by_category.csv'

df_hourly_counts_cloudy_path = f'{output_folder}hourly_counts_cloudy.csv'
df_monthly_counts_cloudy_path = f'{output_folder}monthly_counts_cloudy.csv'
df_hourly_counts_path = f'{output_folder}hourly_counts.csv'

# Plot normalized histogram after processing all files
#plot_normalized_histogram(aggregated_counts, total_points_by_category, output_folder)
#plot_monthly_granular_distribution(monthly_counts, output_folder) 

#plot the normalized histogram from the csv file
plot_normalized_histogram_from_csv(aggregated_counts_path , total_points_by_category_path, output_folder)
plot_temporal_granular_distribution_from_csv(monthly_counts_path, output_folder, 'Month', df_monthly_counts_cloudy_path)
plot_temporal_granular_distribution_from_csv(df_hourly_counts_path, output_folder, 'Hour', df_hourly_counts_cloudy_path)