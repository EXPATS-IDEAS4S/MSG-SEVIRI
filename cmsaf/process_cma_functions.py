import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
from scipy.spatial import cKDTree
import seaborn as sns
import pandas as pd


def plot_monthly_granular_distribution_from_csv(csv_file_path, output_folder):
    """
    Reads monthly granular counts from a CSV file and plots a histogram of the monthly distribution for 3x3 and 5x5 filters.

    Parameters:
    - csv_file_path (str): Path to the CSV file containing the monthly granular point counts for 3x3 and 5x5 filters.
    - output_folder (str): Path to save the output plot.
    """
    # Read CSV file into a DataFrame
    df = pd.read_csv(csv_file_path)
    
    # Rename the columns if necessary (assuming '3x3' and '5x5' are the filter columns)
    df.columns = ['Month', '3x3', '5x5']
    
    # Melt the DataFrame to have 'Month', 'Filter', and 'Count' columns for easy plotting
    df_melted = df.melt(id_vars=['Month'], var_name='Filter', value_name='Count')
    
    # Convert Month to a categorical type with sorted order to ensure chronological display in the plot
    df_melted['Month'] = pd.Categorical(df_melted['Month'], categories=sorted(df['Month'].unique()), ordered=True)
    
    # Initialize Seaborn barplot with Month on x-axis, Count on y-axis, and color by Filter
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df_melted, x='Month', y='Count', hue='Filter', palette={'3x3': 'lightblue', '5x5': 'orange'})

    # Customize plot aesthetics
    plt.xticks(rotation=45)
    plt.ylabel("Granular Point Count")
    plt.xlabel("Month")
    plt.title("Monthly Distribution of Granular Points by Filter")
    plt.legend(title="Filter")
    plt.tight_layout()
    
    # Save plot
    plt.savefig(f'{output_folder}/cloud_mask_holes_distr_by_month_seaborn.png')
    #plt.show()


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
    categories = df_aggregated_counts.columns.tolist()
    
    # Calculate normalized counts
    normalized_counts = pd.DataFrame({
        '3x3': df_aggregated_counts.loc['3x3'] / df_total_points['Total_Points'],
        '5x5': df_aggregated_counts.loc['5x5'] / df_total_points['Total_Points']
    }).reset_index().melt(id_vars='index', var_name='Filter', value_name='Normalized_Count')

    # Rename 'index' column for clarity
    normalized_counts = normalized_counts.rename(columns={'index': 'Elevation_Category'})

    # Plot with Seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(data=normalized_counts, x='Elevation_Category', y='Normalized_Count', hue='Filter', 
                palette={'3x3': 'skyblue', '5x5': 'salmon'})

    # Customize plot
    plt.xlabel('Elevation Category')
    plt.ylabel('Proportion of Granular Points')
    plt.title('Normalized Granular Point Distribution by Elevation for 3x3 and 5x5 Filters')
    plt.legend(title="Filter")
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