import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import cartopy.crs as ccrs
import cartopy.feature as cfeature

CATEGORY_LABELS = {
    0: "Snow",
    42: "Cloud",
    85: "Land",
    170: "Sea",
    212: "Dark",
    233: "No Data",
    255: "Space"
}

# Plot normalized counts of each category across all files
def plot_normalized_counts(dataset, output_folder):
    # Flatten the dataset to count categories
    flat_data = dataset['value'].values.flatten()
    unique, counts = np.unique(flat_data, return_counts=True)

    # Calculate normalized counts
    total = np.sum(counts)
    normalized_counts = counts / total

    # Map the categories and values
    categories = [CATEGORY_LABELS.get(value, "Unknown") for value in unique]

    # Plot
    plt.figure(figsize=(8, 5))
    plt.bar(categories, normalized_counts, color="skyblue")
    plt.xlabel("Category", fontsize=12)
    plt.ylabel("Normalized Count", fontsize=12)
    plt.title("Normalized Count of Each Category", fontsize=14)
    plt.xticks(rotation=45, fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{output_folder}/normalized_counts.png")
    plt.close()

# Count "Snow" category (value 0) per month
def count_snow_by_month(dataset, output_folder, category_value, category_name):
    # get total numer of points
    tot_points = len(dataset['value'].values.flatten())

    # Select only "Snow" category
    snow_data = (dataset['value'] == category_value).astype(int)

    # Extract the month from the 'time' dimension and add it to the DataArray
    snow_data['month'] = snow_data['time'].dt.month

    # Group by the 'month' and sum over 'lat' and 'lon' to get monthly counts
    snow_by_month = snow_data.groupby("month").sum(dim=["lat", "lon"])
    
    # Convert to a DataFrame
    df = snow_by_month.to_dataframe(name="Count").reset_index()
    df = df.groupby('month')['Count'].sum().reset_index()

    # Normalize by dividing the snow count by total number of points
    df['Normalized Count'] = df['Count'] / tot_points


    #remove line with october
    df = df[df["month"] != 10]

    # Plot the monthly snow count
    plt.figure(figsize=(8, 5))
    plt.bar(df["month"], df["Normalized Count"], color="skyblue")
    plt.xlabel("Month", fontsize=12)
    plt.ylabel(f"Normalized {category_name} Count",fontsize=12)
    plt.title(f"Monthly {category_name} Counts",fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.tight_layout()
    plt.savefig(f"{output_folder}/monthly_{category_name}_count_normalized.png")
    plt.close()

    return df

def plot_snow_spatial_distribution_with_geography(datasets, category_value, category_name, output_folder):
    """
    Plots the spatial distribution of the normalized snow counts for each grid cell 
    across multiple files using Cartopy to add geographical features.

    Args:
    - datasets: List of xarray DataArrays (one per file).
    - category_value: The value representing snow (e.g., 0 for snow).
    - category_name: A string representing the category name, e.g., 'Snow'.
    - output_folder: Folder to save the output plot.
    """

    # Initialize an array to accumulate snow counts for each grid point
    snow_counts = None
    total_points = 0

    # Loop through each dataset to accumulate snow counts
    for dataset in datasets:
        # Select only "Snow" category
        snow_data = (dataset['value'] == category_value).astype(int)

        # Sum across the time dimension to count snow occurrences for each grid cell
        snow_sum = snow_data.sum(dim="time")

        # Accumulate snow counts
        if snow_counts is None:
            snow_counts = snow_sum
        else:
            snow_counts += snow_sum

        # Track the total number of points (excluding masked values)
        total_points += snow_data.notnull().sum()

    # Normalize snow counts by the total number of points
    normalized_snow_counts = snow_counts / total_points

    # Plotting with Cartopy
    fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Set up the map with Cartopy features
    ax.set_title(f"Spatial Distribution of {category_name}", fontsize=14)
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    
    # Add geographical features
    ax.add_feature(cfeature.COASTLINE, edgecolor='black')
    ax.add_feature(cfeature.BORDERS, edgecolor='black', linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='gray', facecolor='lightgray')
    ax.add_feature(cfeature.LAND, facecolor='lightgray')
    ax.add_feature(cfeature.LAKES, edgecolor='blue', facecolor='lightblue')

    # Plot the snow counts using imshow with normalized data
    im = ax.imshow(normalized_snow_counts, origin='lower', cmap='Blues', extent=dataset.coords['lon'].values[[0, -1]] + dataset.coords['lat'].values[[0, -1]])
    
    # Add a colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', fraction=0.03, pad=0.04)
    cbar.set_label(f'Normalized {category_name} Count')

    # Save the plot
    plt.tight_layout()
    plt.savefig(f"{output_folder}/spatial_{category_name}_distribution_with_geography.png")
    plt.close()

    return normalized_snow_counts

# Run the function
folder_path = "/data/sat/msg/H_SAF/H10_nc/"

#get list of filename
hsaf_files = sorted(glob(folder_path+'*/*.nc'))
print(len(hsaf_files))
exit()

#open dataset usinf xarray
# Open and merge files along the time dimension
merged_data = xr.open_mfdataset(
        hsaf_files, 
        combine='nested', 
        concat_dim='time', 
        parallel=True     
    )
print(merged_data)

output_folder = '/data/sat/msg/H_SAF/H10_fig/'
os.makedirs(output_folder, exist_ok=True)

#plot_normalized_counts(merged_data, output_folder)
df = count_snow_by_month(merged_data,output_folder,233,'no_data')
print(df)
