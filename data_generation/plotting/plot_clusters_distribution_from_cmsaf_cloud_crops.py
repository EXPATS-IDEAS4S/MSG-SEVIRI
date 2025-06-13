import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from glob import glob
import xarray as xr
import random
import numpy as np

run_name = '10th-90th'

# Paths to CMSAF cloud properties crops
cloud_properties_path = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/nc_clouds/'
cloud_properties_crop_list = sorted(glob(cloud_properties_path + '*.nc')) #crops are read in order by the ML model

# Path to cluster assignments of crops
labels_path = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/features/{run_name}/assignments_800ep.pt'

# Path to cluster distances (from centroids)
distances_path = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/features/{run_name}/distance_800ep.pt'

# Path to fig folder for outputs
output_path = f'/home/dcorradi/Documents/Fig/runs/{run_name}/'

# Define sampling type
sampling_type = 'closest'  # Options: 'random', 'closest', 'farthest', 'all'

# Read data
n_samples = len(cloud_properties_crop_list)
n_subsample = 100  # Number of samples per cluster
n_subsample = min(n_subsample, n_samples)  # Ensure it doesn't exceed available samples

assignments = torch.load(labels_path, map_location='cpu')  # Cluster labels for each sample
distances = torch.load(distances_path, map_location='cpu')  # Distances to cluster centroids

# Convert to numpy arrays for easier manipulation
assignments = assignments[0].cpu().numpy()
distances = distances[0].cpu().numpy()

# Get unique cluster labels
unique_clusters = np.unique(assignments)
print(unique_clusters)

# Prepare a list for subsample indices
subsample_indices = []

# Loop over each cluster and sample data
for cluster in unique_clusters:
    # Get indices for all samples in this cluster
    cluster_indices = np.where(assignments == cluster)[0]
    
    # Get distances for the samples in this cluster
    cluster_distances = distances[cluster_indices]

    # Determine subsample for this cluster based on sampling_type
    if sampling_type == 'random':
        # Randomly select indices from the current cluster
        if len(cluster_indices) <= n_subsample:
            selected_indices = cluster_indices
        else:
            selected_indices = np.random.choice(cluster_indices, n_subsample, replace=False)
    
    elif sampling_type == 'closest':
        # Sort by distance (ascending) and select the closest ones
        sorted_idx = np.argsort(cluster_distances)
        selected_indices = cluster_indices[sorted_idx[:n_subsample]]
    
    elif sampling_type == 'farthest':
        # Sort by distance (descending) and select the farthest ones
        sorted_idx = np.argsort(cluster_distances)
        selected_indices = cluster_indices[sorted_idx[-n_subsample:]]
    
    elif sampling_type == 'all':
        # Use all the available data from this cluster (up to n_subsample if specified)
        selected_indices = cluster_indices#[:n_subsample]
    
    else:
        raise ValueError("Invalid sampling type. Choose from 'random', 'closest', 'farthest', or 'all'.")
    
    # Add selected indices to the subsample list
    subsample_indices.extend(selected_indices)

# Now, create the DataFrame with the selected subsamples
df_labels = pd.DataFrame({
    'path': [cloud_properties_crop_list[i] for i in subsample_indices],
    'label': [assignments[i] for i in subsample_indices]  # The labels of the subsamples
})

# Filter out invalid labels (-100)
df_labels = df_labels[df_labels['label'] != -100]

print(df_labels)


##########################################################
## Compute stats and plot distr for Continous variables ##
##########################################################

continuous_vars = ['cwp', 'cot','ctt', 'ctp', 'cth', 'cre']
cont_vars_long_name = ['cloud water path', 'cloud optical thickness', 'cloud top temperature', 'cloud top pressure', 'cloud top height', 'cloud particle effective radius']
cont_vars_units = ['kg/m^2', '' , 'K', 'hPa', 'm', 'm']
cont_vars_logscale = [False, False, False, False, False, False]
cont_vars_dir = ['incr','incr', 'decr','decr','incr', 'incr']

# Initialize lists to hold data for continuous and categorical variables
continuous_data = {var: [] for var in continuous_vars}
labels = []

# Read the .nc files and extract data
for i, row in df_labels.iterrows():
    ds = xr.open_dataset(row['path'])
    
    for var in continuous_vars:
        continuous_data[var].extend(ds[var].values.flatten())
    
    labels.extend([row['label']] * ds[continuous_vars[0]].values.size)

# Create DataFrames for continuous and categorical variables
df_continuous = pd.DataFrame(continuous_data)
df_continuous['label'] = labels



# Compute stats for continuous variables
continuous_stats = df_continuous.groupby('label').agg(['mean', 'std'])
continuous_stats.columns = ['_'.join(col).strip() for col in continuous_stats.columns.values]
continuous_stats.reset_index(inplace=True)

# Save continuous stats to a CSV file
continuous_stats.to_csv(f'{output_path}continuous_stats.csv', index=False)
print('Continous Stats saved to CSV files.')

# Plotting continuous variables box plots
for var, long_name, unit, direction, scale in zip(continuous_vars, cont_vars_long_name, cont_vars_units, cont_vars_dir, cont_vars_logscale):
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=df_continuous, x='label', y=var, ax=ax, showfliers=False)
    plt.title(f'Boxplot of {long_name} ({var}) - {n_subsample} samples')
    plt.xlabel('Cloud Class Label')
    plt.ylabel(f'{long_name} ({unit})')
    if scale:
        plt.yscale('log')
    
        # Exclude zero values
        non_zero_values = df_continuous[df_continuous[var] > 0][var]

        # Find the minimum of the non-zero values
        min_non_zero = non_zero_values.min()
        print(min_non_zero)
        #set y lim
        plt.ylim(bottom=min_non_zero)


    # Reverse y axis if direction is 'decr'
    if direction == 'decr':
        ax.invert_yaxis()
    
    # Save the figure
    fig.savefig(f'{output_path}{var}_boxplot_{n_subsample}.png', bbox_inches='tight')
    print(f'Figure saved: {output_path}{var}_boxplot_{n_subsample}.png')


############################################################
## Compute stats and plot distr for Categorical variables ##
############################################################

categorical_vars = ['cph', 'cma']
cat_vars_long_name = ['cloud phase', 'cloud mask']
#cat_var_units = [('clear','liquid','ice'),('clear','cloudy')]

# Initialize lists to hold data for continuous and categorical variables
categorical_data = {var: [] for var in categorical_vars}
labels = []

# Read the .nc files and extract data
for i, row in df_labels.iterrows():
    ds = xr.open_dataset(row['path'])
        
    for var in categorical_vars:
        categorical_data[var].extend(ds[var].values.flatten())
    
    labels.extend([row['label']] * ds[categorical_vars[0]].values.size)

# Create DataFrames for continuous and categorical variables
df_categorical = pd.DataFrame(categorical_data)
df_categorical['label'] = labels

print(df_categorical)

# Compute stats for categorical variables excluding the label column
categorical_percentages = df_categorical.groupby('label').apply(
    lambda x: x.drop(columns='label').apply(lambda col: col.value_counts(normalize=True))
)
print(categorical_percentages)

df_cat_stats = pd.DataFrame(categorical_percentages)

# Save categorical stats to a CSV file
df_cat_stats.to_csv(f'{output_path}categorical_stats.csv', index=False)

#Compute relative frequency of each label
label_counts = df_categorical['label'].value_counts(normalize=True) * 100

print(label_counts)

df_rel_freq = pd.DataFrame(label_counts)

# Save categorical stats to a CSV file
df_rel_freq.to_csv(f'{output_path}label_rel_freq.csv', index=False)


# Define a function to compute the percentage of cloudy points based on cma variable
def compute_cloudy_percentage(image_path):
    # Load the image assuming it's a numpy array file with 'cma' variable
    data = xr.open_dataset(image_path)
    cma = data['cma'].values  # Extract the 'cma' array
    cloudy_points = np.sum(cma == 1)
    total_points = len(cma.flatten())
    return (cloudy_points / total_points) * 100

# Apply the function to each crop and store results in a new column
df_labels['cloudy_percentage'] = df_labels['path'].apply(compute_cloudy_percentage)

# Group by label and compute mean and std of cloudy percentages
stats = df_labels.groupby('label')['cloudy_percentage'].agg(['mean', 'std']).reset_index()

print(stats)



# Mapping dictionaries
cph_mapping = {0: 'clear', 1: 'liquid', 2: 'ice'}
cma_mapping = {0: 'clear', 1: 'cloudy'}

# Adding new columns
df_categorical['cph_name'] = df_categorical['cph'].map(cph_mapping)
df_categorical['cma_name'] = df_categorical['cma'].map(cma_mapping)

print(df_categorical)

# Plotting categorical
for var, long_name in zip(categorical_vars, cat_vars_long_name):
    fig, axes = plt.subplots(1, 1, figsize=(14, 6), sharey=True)
    sns.countplot(df_categorical, x='label', hue=var+'_name')#, stat='percent')
    axes.set_title(f'{long_name} Occurrence by Label')
    axes.set_ylabel('Counts')
    axes.set_xlabel('Label')
    fig.savefig(f'{output_path}{var}_bar_{n_subsample}.png', bbox_inches='tight')
    print(f'Figure saved: {output_path}{var}_bar_{n_subsample}.png')

