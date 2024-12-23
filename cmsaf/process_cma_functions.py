import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from scipy.spatial import cKDTree
import seaborn as sns
import pandas as pd
import xarray as xr
from glob import glob
import os



def plot_temporal_granular_distribution_from_csv(csv_file_path, output_folder, time_label, total_csv_file_path=None):
    """
    Reads monthly or hourly granular counts and total counts from CSV files, normalizes the counts, and plots a histogram 
    of the normalized temporal distribution for 3x3 and 5x5 filters.

    Parameters:
    - csv_file_path (str): Path to the CSV file containing the granular point counts for 3x3 and 5x5 filters.
    - total_csv_file_path (str): Path to the CSV file containing the total counts for normalization.
    - output_folder (str): Path to save the output plot.
    - time_label (str): Label for the time dimension (e.g., 'Month', 'Hour').
    """
    # Read both CSV files
    df_counts = pd.read_csv(csv_file_path, index_col=0).T  # Monthly counts, transposed
    
    # Reset index to make 'Month' a column in each DataFrame
    df_counts = df_counts.reset_index().rename(columns={'index': time_label})

    # If path to total counts CSV is provided, normalize the counts by the total counts
    if total_csv_file_path:
        df_totals = pd.read_csv(total_csv_file_path, index_col=0).T  # Total counts, transposed to match structure
        df_totals = df_totals.reset_index().rename(columns={'index': time_label})
        df_counts['5x5'] = df_counts['5x5'] / df_totals['5x5']
        df_counts['3x3'] = df_counts['3x3'] / df_totals['3x3']

    
    # Reshape data to long format for plotting
    df_long = pd.DataFrame({
        time_label: pd.concat([df_counts[time_label], df_counts[time_label]], ignore_index=True),
        'Filter': ['3x3'] * len(df_counts) + ['5x5'] * len(df_counts),
        'Normalized Count': pd.concat([df_counts['3x3'], df_counts['5x5']], ignore_index=True)
    })

    # Ensure Month is treated as a categorical type for proper ordering in the plot
    df_long[time_label] = pd.Categorical(df_long[time_label], categories=sorted(df_long[time_label].unique()), ordered=True)

    # Plotting the normalized counts
    if time_label=='Month':
        figsize = (7, 4)
    elif time_label=='Hour':
        figsize = (9, 4)
    plt.figure(figsize=figsize)
    sns.barplot(data=df_long, x=time_label, y='Normalized Count', hue='Filter', palette={'3x3': 'lightblue', '5x5': 'orange'})

    # Customize plot aesthetics
    plt.xticks(rotation=45, fontsize=14)
    plt.yticks(fontsize=14) 
    plt.xlabel(time_label, fontsize=14)
    if total_csv_file_path:
        plt.ylabel("Normalized Count", fontsize=14)
        filename_save_path = f'{output_folder}/normalized_cloud_mask_holes_distr_by_{time_label}.png'
        plt.title(f"Normalized {time_label}ly Distribution of Granular Points", fontsize=15, fontweight='bold')
    else:
        plt.ylabel("Count", fontsize=14)
        filename_save_path = f'{output_folder}/cloud_mask_holes_distr_by_{time_label}.png'
        plt.title(f"{time_label}ly Distribution of Granular Points", fontsize=15, fontweight='bold')

    # Position legend outside the plot on the right
    plt.legend(title="Filter", title_fontsize='13', fontsize='11', loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()

    # Save plot
    plt.savefig(filename_save_path)
    # plt.show()  # Uncomment to display the plot


def plot_monthly_granular_distribution(monthly_counts, output_folder):
    """
    Plots a histogram of the monthly distribution of granular points for 3x3 and 5x5 filters.
    
    Parameters:
    - monthly_counts (dict): Dictionary with monthly granular point counts for 3x3 and 5x5 filters.
                             Format: {'3x3': {'MM': count, ...}, '5x5': {'MM': count, ...}}
    """
    # Sort months to ensure the histogram is in chronological order
    months = sorted(monthly_counts['3x3'].keys())
    
    # Prepare data for the plot
    counts_3x3 = [monthly_counts['3x3'][month] for month in months]
    counts_5x5 = [monthly_counts['5x5'][month] for month in months]
    
    # Convert months to readable labels
    month_labels = [f"{month}" for month in months]

    # Plot histogram
    x = range(len(months))  # Position of bars

    fig, axes = plt.subplots(figsize=(12, 6))
    plt.bar(x, counts_3x3, width=0.4, label="3x3 Filter", color='lightblue', align='center')
    plt.bar(x, counts_5x5, width=0.4, label="5x5 Filter", color='orange', align='edge')

    plt.xticks(x, month_labels, rotation=45)
    plt.ylabel("Granular Point Count")
    plt.title("Monthly Distribution of Granular Points by Filter")
    plt.legend()
    plt.tight_layout()
    plt.show()
    fig.savefig(f'{output_folder}cloud_mask_holes_distr_by_month.png')


def plot_normalized_histogram_from_csv(aggregated_counts_csv, total_points_csv, output_folder):
    """
    Reads aggregated counts and total points by category from CSV files, and plots a normalized bar chart
    of granular counts across elevation categories for 3x3 and 5x5 masks.

    Parameters:
    - aggregated_counts_csv (str): Path to the CSV file containing the cumulative granular counts.
    - total_points_csv (str): Path to the CSV file containing the total points in each elevation category.
    - output_folder (str): Path to save the output plot.
    """
    # Load CSV files
    df_aggregated_counts = pd.read_csv(aggregated_counts_csv, index_col=0)
    df_total_points = pd.read_csv(total_points_csv, index_col=0)

    # Define categories
    #categories = df_aggregated_counts.columns.tolist()
    
    # Calculate normalized counts
    normalized_counts = pd.DataFrame({
        '3x3': df_aggregated_counts.loc['3x3'] / df_total_points['Total_Points'],
        '5x5': df_aggregated_counts.loc['5x5'] / df_total_points['Total_Points']
    }).reset_index().melt(id_vars='index', var_name='Filter', value_name='Normalized_Count')

    # Rename 'index' column for clarity
    normalized_counts = normalized_counts.rename(columns={'index': 'Elevation_Category'})

    # Plot with Seaborn
    plt.figure(figsize=(7, 4))
    sns.barplot(data=normalized_counts, x='Elevation_Category', y='Normalized_Count', hue='Filter', 
                palette={'3x3': 'lightblue', '5x5': 'orange'})

    # Customize plot
    plt.xlabel('Elevation Category', fontsize=14)
    plt.ylabel('Normalized Count',fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.title('Normalized Granular Point Distribution by Elevation', fontsize=15, fontweight='bold')
    plt.legend(title="Filter", title_fontsize='13', fontsize='11', loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(f'{output_folder}/cloud_mask_holes_distr_by_elev_categ_seaborn.png')
    #plt.show()




def plot_normalized_histogram(aggregated_counts, total_points_by_category, output_folder):
    """
    Plots a normalized bar chart of granular counts across elevation categories for 3x3 and 5x5 masks.

    Parameters:
    - aggregated_counts (dict): Cumulative granular counts in format:
      {'3x3': {'flat': total_count, 'hills': total_count, 'mountains': total_count},
       '5x5': {'flat': total_count, 'hills': total_count, 'mountains': total_count}}
    - total_points_by_category (dict): Total points in each elevation category
      {'flat': total_count, 'hills': total_count, 'mountains': total_count}
    """
    categories = ['flat', 'hills', 'mountains']
    
    # Normalize counts for each mask type by total points in each category
    normalized_counts_3x3 = [aggregated_counts['3x3'][cat] / total_points_by_category[cat] for cat in categories]
    normalized_counts_5x5 = [aggregated_counts['5x5'][cat] / total_points_by_category[cat] for cat in categories]

    # Set up bar positions
    bar_width = 0.35
    x = np.arange(len(categories))

    # Plot bars for 3x3 and 5x5
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - bar_width / 2, normalized_counts_3x3, bar_width, label='3x3', color='skyblue')
    ax.bar(x + bar_width / 2, normalized_counts_5x5, bar_width, label='5x5', color='salmon')

    # Add labels and legend
    ax.set_xlabel('Elevation Category')
    ax.set_ylabel('Proportion of Granular Points')
    ax.set_title('Normalized Granular Point Distribution by Elevation for 3x3 and 5x5 Filters')
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()

    # Show plot
    plt.tight_layout()
    #plt.show()
    fig.savefig(f'{output_folder}cloud_mask_holes_distr_by_elev_categ.png')



def count_granular_points_by_orography(granular_mask_3x3, granular_mask_5x5, lat, lon, ds_orography):
    """
    Counts the number of granular points in each orographic category (flat, hills, mountains) for both 3x3 and 5x5 masks.

    Parameters:
    - granular_mask_3x3 (ndarray): Granular regions identified in the (3x3) closed cloud mask.
    - granular_mask_5x5 (ndarray): Granular regions identified in the (5x5) closed cloud mask.
    - lat (ndarray): Latitude array of the cloud mask.
    - lon (ndarray): Longitude array of the cloud mask.
    - ds_orography (xarray.Dataset): Orography dataset with a variable named 'elevation' (in meters) and coordinates 'lat' and 'lon'.
    
    Returns:
    - dict: A dictionary with counts of granular points in each orographic level for 3x3 and 5x5 masks.
            Format: {
                '3x3': {'flat': int, 'hills': int, 'mountains': int},
                '5x5': {'flat': int, 'hills': int, 'mountains': int}
            }
    """
    
    # Define elevation categories in meters
    flat_threshold = 200
    hill_threshold = 600
    
    # Flatten the latitude and longitude arrays for cloud mask
    lon_grid, lat_grid = np.meshgrid(lon, lat, indexing='ij')
    cloud_mask_points = np.array([lat_grid.ravel(), lon_grid.ravel()]).T
    
    # Create KDTree from orography dataset coordinates for fast nearest-neighbor lookup
    lat_oro = ds_orography['lat'].values
    lon_oro = ds_orography['lon'].values
    lon_grid_oro, lat_grid_oro = np.meshgrid(lon_oro, lat_oro,indexing='ij')
    orography_points = np.array([lat_grid_oro.ravel(), lon_grid_oro.ravel()]).T
    tree = cKDTree(orography_points)
    
    # Find closest orography points for each cloud mask point
    _, indices = tree.query(cloud_mask_points)
    
    # Get elevation values at nearest points
    elevation = ds_orography['DEM'].values.ravel()[indices].reshape(lat_grid.shape)
    
    # Initialize counters for each category and mask
    counts = {
        '3x3': {'flat': 0, 'hills': 0, 'mountains': 0},
        '5x5': {'flat': 0, 'hills': 0, 'mountains': 0}
    }
    
    total_points = {'flat': 0, 'hills': 0, 'mountains': 0}
    
    # Define function to categorize elevation
    def categorize(elevation_value):
        if elevation_value < flat_threshold:
            return 'flat'
        elif elevation_value < hill_threshold:
            return 'hills'
        else:
            return 'mountains'
    
    # Count total points by category
    for i in range(lat_grid.shape[0]):
        for j in range(lat_grid.shape[1]):
            category = categorize(elevation[i, j])
            total_points[category] += 1
    
    # Count granular points for the 3x3 mask
    for i, j in zip(*np.where(granular_mask_3x3)):
        category = categorize(elevation[i, j])
        counts['3x3'][category] += 1
    
    # Count granular points for the 5x5 mask
    for i, j in zip(*np.where(granular_mask_5x5)):
        category = categorize(elevation[i, j])
        counts['5x5'][category] += 1
    
    return counts, total_points



def plot_cloud_mask(cloud_mask, closed_mask_3x3, closed_mask_5x5, granular_mask_3x3, granular_mask_5x5, num_features_3x3, num_features_5x5, date, lat, lon, output_folder):
    """
    Plots cloud mask data with various closing operations to fill granular cloud regions, saving the output as a PNG.

    This function visualizes the original cloud mask, a closed mask with a (3x3) structuring element, 
    and a closed mask with a (5x5) structuring element in a single row of subplots. The closed granular 
    regions are highlighted in orange, with different counts of closed regions displayed in the titles. 
    Each plot includes geographic borders and coastlines for context.

    Parameters:
    - cloud_mask (ndarray): Original cloud mask data (0 for clear, 1 for cloudy).
    - closed_mask_3x3 (ndarray): Cloud mask after closing with a (3x3) structuring element.
    - closed_mask_5x5 (ndarray): Cloud mask after closing with a (5x5) structuring element.
    - granular_mask_3x3 (ndarray): Granular regions identified in the (3x3) closed mask.
    - granular_mask_5x5 (ndarray): Granular regions identified in the (5x5) closed mask.
    - num_features_3x3 (int): Number of identified granular regions in the (3x3) closed mask.
    - num_features_5x5 (int): Number of identified granular regions in the (5x5) closed mask.
    - date (str): Date string extracted from the filename for display and saving.
    - lat (ndarray): Array of latitude values, used to set map extent.
    - lon (ndarray): Array of longitude values, used to set map extent.
    - output_folder (str): Folder path where the output plot image will be saved.

    Returns:
    - None: Saves the generated plot as a PNG file in the specified output folder.
    """
        
    # Set up the plot with 3 subplots in a row and Cartopy projection
    fig, ax = plt.subplots(1, 3, figsize=(18, 7), subplot_kw={'projection': ccrs.PlateCarree()})
    fig.suptitle(f"Filling Cloud Mask: {date}", fontsize=16)

    # Define color map for clear (0), cloudy (1)
    colors = {0: 'lightblue', 1: 'gray'}
    cmap = plt.matplotlib.colors.ListedColormap([colors[0], colors[1]])
    bounds = [0, 1, 2]
    norm = plt.matplotlib.colors.BoundaryNorm(bounds, cmap.N)

    # Plot the original cloud mask
    ax[0].imshow(cloud_mask, extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                cmap=cmap, norm=norm, origin='upper', interpolation='none')
    ax[0].set_title("Original Cloud Mask")
    ax[0].add_feature(cfeature.BORDERS, linestyle='-', alpha=0.5)
    ax[0].add_feature(cfeature.COASTLINE)
    ax[0].set_extent([lon.min(), lon.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree())

    # Plot closed cloud mask with (3, 3) structure
    ax[1].imshow(closed_mask_3x3, extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                cmap=cmap, norm=norm, origin='upper', interpolation='none')
    ax[1].imshow(granular_mask_3x3, extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                cmap='Oranges', origin='upper', alpha=0.5)  # Overlay colored patches on original
    ax[1].set_title(f"Closed Cloud Mask (3x3) (Count: {num_features_3x3})")
    ax[1].add_feature(cfeature.BORDERS, linestyle='-', alpha=0.5)
    ax[1].add_feature(cfeature.COASTLINE)
    ax[1].set_extent([lon.min(), lon.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree())

    # Plot closed cloud mask with (5, 5) structure
    ax[2].imshow(closed_mask_5x5, extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                cmap=cmap, norm=norm, origin='upper', interpolation='none')
    ax[2].imshow(granular_mask_5x5, extent=[lon.min(), lon.max(), lat.min(), lat.max()],
                cmap='Oranges', origin='upper', alpha=0.5)  # Overlay colored patches on original
    ax[2].set_title(f"Closed Cloud Mask (5x5): (Count: {num_features_5x5})")
    ax[2].add_feature(cfeature.BORDERS, linestyle='-', alpha=0.5)
    ax[2].add_feature(cfeature.COASTLINE)
    ax[2].set_extent([lon.min(), lon.max(), lat.min(), lat.max()], crs=ccrs.PlateCarree())

    # Add a legend outside the plot on the right
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors[0], edgecolor='black', label='Clear Pixels'),
        Patch(facecolor=colors[1], edgecolor='black', label='Cloudy Pixels'),
        Patch(facecolor='orange', edgecolor='black', label='Closed Pixels')
    ]
    fig.legend(handles=legend_elements, loc='upper left', frameon=True)

    plt.tight_layout()#rect=[0, 0, 0.9, 0.95])  # Adjust layout to fit legend

    # Save the plot
    fig.savefig(f'{output_folder}cloud_mask_{date}.png')



def find_cma_file(cma_product_path, time_str):
    """
    Finds the corresponding CMA file based on the provided time string.

    Args:
        cma_product_path (str): Path to the directory containing CMA product files.
        time_str (str): Time string in the format 'yyyy-mm-ddThh:mm', used to identify the matching CMA file.

    Returns:
        str: Path to the first matching CMA file found, or None if no matching file is found.
    """

    # Function to find the corresponding CMA file based on time
    year, month, day, hh, mm = time_str[:4], time_str[5:7], time_str[8:10], time_str[11:13], time_str[14:16]
    #print(f"Year: {year}, Month: {month}, Day: {day}, Hour: {hh}, Minute: {mm}")
    folder_path = os.path.join(cma_product_path, year, month, day)
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return None

    # Find the file with matching time
    hhmm = hh + mm
    file_pattern = f"CMAin{year}{month}{day}{hhmm}*.nc"
    matching_files = glob(os.path.join(folder_path, file_pattern))
    if matching_files:
        return matching_files[0]
    else:
        print(f"No matching file found for {file_pattern}")
        return None


def extract_data(nc_file, cma_product_path):
    """
    Extracts the CMA dataset for the given crop dataset file based on matching latitude, 
    longitude, and time information.

    Args:
        nc_file (str): Path to the crop dataset netCDF file.
        cma_product_path (str): Path to the directory containing the CMA product files.

    Returns:
        xarray.Dataset: A subset of the CMA dataset corresponding to the latitude, longitude, 
                        and time of the given crop dataset, or None if no matching CMA file is found.
    """

    # Open dataset of the crop and extract coordinates
    ds = xr.open_dataset(nc_file)
    time = ds.time.values
    lat = ds.lat.values
    lon = ds.lon.values
    #print(f"Time: {time}")
    #print(f"Lat: {lat.min()}, {lat.max()}")
    #print(f"Lon: {lon.min()}, {lon.max()}")

    # Find the corresponding CMA file      
    cma_file = find_cma_file(cma_product_path, str(time))
    print(f"CMA file: {cma_file}")
    if cma_file:
        cma_ds = xr.open_dataset(cma_file)
        #print(cma_ds)

        #Slice ds based on lat lon
        cma_ds = cma_ds.sel(lat=lat, lon=lon, method='nearest')
        #print(cma_ds)

        return cma_ds
    else:
        print("No CMA file found")
        return None
      