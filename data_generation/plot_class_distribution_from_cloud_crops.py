import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import torch
from glob import glob
import xarray as xr

# Paths
cloud_properties_path = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc_clouds/'
cloud_properties_crop_list = sorted(glob(cloud_properties_path + '*.nc'))
labels_path = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/assignments_800ep.pt'
output_path = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/'

n_samples = len(cloud_properties_crop_list)

# Variables
categorical_vars = ['cph', 'cma']
continuous_vars = ['cwp', 'cot', 'ctt', 'ctp', 'cth']

# Read the labels
assignments = torch.load(labels_path, map_location='cpu')

# Create DataFrame for paths and labels
df_labels = pd.DataFrame({
    'path': cloud_properties_crop_list,
    'label': [assignments[0].cpu()[i].item() for i in range(len(cloud_properties_crop_list))]
})

# Initialize lists to hold data for continuous and categorical variables
continuous_data = {var: [] for var in continuous_vars}
categorical_data = {var: [] for var in categorical_vars}
labels = []

# Read the .nc files and extract data
for i, row in df_labels.iterrows():
    ds = xr.open_dataset(row['path'])
    
    for var in continuous_vars:
        continuous_data[var].extend(ds[var].values.flatten())
        
    for var in categorical_vars:
        categorical_data[var].extend(ds[var].values.flatten())
    
    labels.extend([row['label']] * ds[categorical_vars[0]].values.size)

# Create DataFrames for continuous and categorical variables
df_continuous = pd.DataFrame(continuous_data)
df_continuous['label'] = labels

df_categorical = pd.DataFrame(categorical_data)
df_categorical['label'] = labels

# Plotting continuous variables distributions
for var in continuous_vars:
    fig, ax = plt.figure(figsize=(10, 6))
    sns.histplot(data=df_continuous, x=var, hue='label', element='step', stat='density', common_norm=False)
    plt.title(f'Distribution of {var} by Label')
    plt.xlabel(var)
    plt.ylabel('Density')
    plt.legend(title='Label')
    #plt.show()
    fig.savefig(f'{output_path}{var}_distr_{n_samples}.png', bbox_inches='tight')

# Plotting categorical variables percentages
for var in categorical_vars:
    fig, ax = plt.figure(figsize=(10, 6))
    df_categorical_grouped = df_categorical.groupby(['label', var]).size().reset_index(name='count')
    total_counts = df_categorical_grouped.groupby('label')['count'].sum().reset_index(name='total')
    df_categorical_grouped = df_categorical_grouped.merge(total_counts, on='label')
    df_categorical_grouped['percentage'] = df_categorical_grouped['count'] / df_categorical_grouped['total'] * 100
    
    sns.barplot(data=df_categorical_grouped, x=var, y='percentage', hue='label')
    plt.title(f'Percentage of {var} Categories by Label')
    plt.xlabel(f'{var} Category')
    plt.ylabel('Percentage')
    plt.legend(title='Label')
    #plt.show()
    fig.savefig(f'{output_path}{var}_distr_{n_samples}.png', bbox_inches='tight')
