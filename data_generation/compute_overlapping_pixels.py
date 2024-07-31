import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
import itertools
import re
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import random

# Paths and parameters
cloud_properties_path = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/nc/'
cloud_properties_crop_list = sorted(glob(cloud_properties_path + '*.nc'))
n_samples_per_timestamp = 4  # Change this to the number of crops per timestamp
output_path = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/'

# Regular expression pattern to match the date and time part
pattern = re.compile(r'/(\d{8}_\d{2}:\d{2})_')

# Extract dates
dates = np.unique([pattern.search(path).group(1) for path in cloud_properties_crop_list])

# Extract 1000 random dates
dates = random.sample(list(dates), 1000)

print(dates)

# Generate the list of random integers
random_integers = random.sample(range(len(dates)), 10)

def compute_overlapping_pixels(crop1, crop2):
    # Find common latitudes and longitudes
    common_lat = np.intersect1d(crop1.lat.values, crop2.lat.values)
    common_lon = np.intersect1d(crop1.lon.values, crop2.lon.values)
    
    # Count the number of common latitudes and longitudes
    overlap_lat = len(common_lat)
    overlap_lon = len(common_lon)
    
    return overlap_lat * overlap_lon

def get_files_with_date(file_paths, date):
    """
    Returns a list of file paths that contain the specified date.

    Parameters:
    file_paths (list): List of file paths.
    date (str): The date to match in the format 'YYYYMMDD_HH:MM'.

    Returns:
    list: List of file paths that contain the specified date.
    """
    # Regular expression pattern to match the date and time part
    pattern = re.compile(r'/(\d{8}_\d{2}:\d{2})_')
    
    # Filter file paths that contain the specified date
    matching_files = [path for path in file_paths if pattern.search(path).group(1) == date]

    return matching_files


# Function to extract boundaries from a dataset
def get_boundaries(ds):
    min_lon = ds.lon.min().item()
    max_lon = ds.lon.max().item()
    min_lat = ds.lat.min().item()
    max_lat = ds.lat.max().item()
    return min_lon, max_lon, min_lat, max_lat


def plot_crops_on_map(crop_boundaries, time, output_path, domain=[5, 16, 42, 51.5]):
    """
    Plots the latitude and longitude boundaries of the crops on a Cartopy map.

    Parameters:
    crop_boundaries (list of tuples): A list of tuples where each tuple contains 
                                      the (min_lon, max_lon, min_lat, max_lat) of a crop.
    domain (list): The domain to plot the crops in the format [min_lon, max_lon, min_lat, max_lat].
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent(domain, crs=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    ax.gridlines(draw_labels=True)
    
    # Plot the crop boundaries
    for (min_lon, max_lon, min_lat, max_lat) in crop_boundaries:
        lons = [min_lon, max_lon, max_lon, min_lon, min_lon]
        lats = [min_lat, min_lat, max_lat, max_lat, min_lat]
        ax.plot(lons, lats, color='red', transform=ccrs.PlateCarree())

    plt.title('Crop Boundaries on Map')
    fig.savefig(f'{output_path}domain_with_crops_{time}.png', bbox_inches='tight')
    print(f'Fig  saved to: {output_path} domain_with_crops_{time}.png')


def plot_subcrops(crop_boundary, time, output_path, pixels=96, domain=[5, 16, 42, 51.5]):
    """
    Plots the latitude and longitude boundaries of a single crop on a Cartopy map
    and includes two 96x96 pixel frames positioned randomly within the crop boundary.

    Parameters:
    crop_boundary (tuple): A tuple containing the (min_lon, max_lon, min_lat, max_lat) of a crop.
    time (str): A string representing the time for the output file name.
    output_path (str): The directory where the plot will be saved.
    domain (list): The domain to plot the crops in the format [min_lon, max_lon, min_lat, max_lat].
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent(domain, crs=ccrs.PlateCarree())
    
    # Add map features
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    ax.gridlines(draw_labels=True)
    
    # Plot the crop boundary
    min_lon, max_lon, min_lat, max_lat = crop_boundary
    lons = [min_lon, max_lon, max_lon, min_lon, min_lon]
    lats = [min_lat, min_lat, max_lat, max_lat, min_lat]
    ax.plot(lons, lats, color='red', transform=ccrs.PlateCarree())
    
    # Define the size of the frames (96x96 pixels) in terms of degrees
    frame_width_deg = 96 * 0.04  # 1 pixel ~ 0.04 degrees
    frame_height_deg = 96 * 0.04
    
    # Function to generate random frame positions within the crop boundary
    def get_random_frame_position(min_lon, max_lon, min_lat, max_lat, frame_width_deg, frame_height_deg):
        lon = random.uniform(min_lon, max_lon - frame_width_deg)
        lat = random.uniform(min_lat, max_lat - frame_height_deg)
        return lon, lon + frame_width_deg, lat, lat + frame_height_deg

    # Plot the first random frame
    frame1_min_lon, frame1_max_lon, frame1_min_lat, frame1_max_lat = get_random_frame_position(
        min_lon, max_lon, min_lat, max_lat, frame_width_deg, frame_height_deg)
    frame1_lons = [frame1_min_lon, frame1_max_lon, frame1_max_lon, frame1_min_lon, frame1_min_lon]
    frame1_lats = [frame1_min_lat, frame1_min_lat, frame1_max_lat, frame1_max_lat, frame1_min_lat]
    ax.plot(frame1_lons, frame1_lats, color='blue', transform=ccrs.PlateCarree())
    
    # Plot the second random frame
    frame2_min_lon, frame2_max_lon, frame2_min_lat, frame2_max_lat = get_random_frame_position(
        min_lon, max_lon, min_lat, max_lat, frame_width_deg, frame_height_deg)
    frame2_lons = [frame2_min_lon, frame2_max_lon, frame2_max_lon, frame2_min_lon, frame2_min_lon]
    frame2_lats = [frame2_min_lat, frame2_min_lat, frame2_max_lat, frame2_max_lat, frame2_min_lat]
    ax.plot(frame2_lons, frame2_lats, color='green', transform=ccrs.PlateCarree())
    
    plt.title('Crop with 2 random subcrops')
    fig.savefig(f'{output_path}subcrops_{time}.png', bbox_inches='tight')
    print(f'Figure saved to: {output_path}subcrops_{time}.png')


def plot_subcrops_in_domain(domain, time, output_path, pixels=96):
    """
    Plots the latitude and longitude boundaries of crops at the four corners of the domain,
    and includes two 96x96 pixel frames positioned randomly within each crop boundary.

    Parameters:
    domain (list): The domain to plot the crops in the format [min_lon, max_lon, min_lat, max_lat].
    time (str): A string representing the time for the output file name.
    output_path (str): The directory where the plot will be saved.
    crop_size_deg (float): Size of each crop in degrees.
    pixels (int): Size of the sub-crops in pixels (assumed to be square).
    """
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.set_extent(domain, crs=ccrs.PlateCarree())

    # Add map features
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.LAKES, alpha=0.5)
    ax.add_feature(cfeature.RIVERS)
    ax.gridlines(draw_labels=True)

    min_lon, max_lon, min_lat, max_lat = domain
    central_lon = (min_lon + max_lon) / 2
    central_lat = (min_lat + max_lat) / 2

    # Define the crop boundaries
    crop_boundaries = [
        (min_lon, central_lon, central_lat, max_lat),  # Upper left
        (central_lon, max_lon, central_lat, max_lat),  # Upper right
        (min_lon, central_lon, min_lat, central_lat),  # Lower left
        (central_lon, max_lon, min_lat, central_lat)   # Lower right
    ]

    # Define the size of the frames (96x96 pixels) in terms of degrees
    frame_width_deg = pixels * 0.04  # 1 pixel ~ 0.04 degrees
    frame_height_deg = pixels * 0.04

    def get_random_frame_position(min_lon, max_lon, min_lat, max_lat, frame_width_deg, frame_height_deg):
        lon = random.uniform(min_lon, max_lon - frame_width_deg)
        lat = random.uniform(min_lat, max_lat - frame_height_deg)
        return lon, lon + frame_width_deg, lat, lat + frame_height_deg

    # Plot the crop boundaries and sub-crops
    for crop_boundary in crop_boundaries:
        # Plot the crop boundary
        min_lon, max_lon, min_lat, max_lat = crop_boundary
        lons = [min_lon, max_lon, max_lon, min_lon, min_lon]
        lats = [min_lat, min_lat, max_lat, max_lat, min_lat]
        ax.plot(lons, lats, color='red', transform=ccrs.PlateCarree())

        # Plot two random sub-crops within the current crop boundary
        for _ in range(2):
            frame_min_lon, frame_max_lon, frame_min_lat, frame_max_lat = get_random_frame_position(
                min_lon, max_lon, min_lat, max_lat, frame_width_deg, frame_height_deg)
            frame_lons = [frame_min_lon, frame_max_lon, frame_max_lon, frame_min_lon, frame_min_lon]
            frame_lats = [frame_min_lat, frame_min_lat, frame_max_lat, frame_max_lat, frame_min_lat]
            ax.plot(frame_lons, frame_lats, color='blue', transform=ccrs.PlateCarree())

    plt.title('Crops with 2 Random Sub-crops Each')
    fig.savefig(f'{output_path}subcrops_equally_divided_{time}.png', bbox_inches='tight')
    print(f'Figure saved to: {output_path}subcrops_{time}.png')

# Initialize an empty list to store overlapping results for each timestamp
overlap_results = []

# Process each timestamp
for i, date in enumerate(dates):
    timestamp_crops = get_files_with_date(cloud_properties_crop_list,date)
    #print(timestamp_crops)
    crops = [xr.open_dataset(crop) for crop in timestamp_crops]
    #print(crops)

    # Extract boundaries for each crop
    crop_boundaries = [get_boundaries(crop) for crop in crops]
    
    if i in random_integers:
        #plot_subcrops_in_domain([5, 16, 42, 51.5],date,output_path)
        plot_crops_on_map(crop_boundaries, date, output_path)
        plot_subcrops(crop_boundaries[0], date, output_path)

    # Compute pairwise overlapping pixels
    overlaps = []
    for crop1, crop2 in itertools.combinations(crops, 2):
        overlap = compute_overlapping_pixels(crop1, crop2)
        #print(overlap)
        overlaps.append(overlap)
    
    overlap_results.append(overlaps)
    #print(overlap_results)

# Convert the results to a NumPy array
# Flatten the list using list comprehension
flattened_results = [item for sublist in overlap_results for item in sublist]

# Convert the flattened list to a NumPy array
overlap_results_array = np.array(flattened_results)
print(overlap_results_array)

np.save(f'{output_path}overlap_results.npy', overlap_results_array)

# Calculate the frequency of each integer value
unique_values, counts = np.unique(overlap_results_array, return_counts=True)

# Plot the bar plot
fig, ax = plt.subplots(figsize=(10, 6))
ax.bar(unique_values, counts, edgecolor='black')
plt.title('Distribution of Overlapping Pixels')
plt.xlabel('Number of Overlapping Pixels')
plt.ylabel('Counts')
plt.yscale('log')
plt.grid(True)

# Optionally, save the overlap results
fig.savefig(f'{output_path}overlap_results.png', bbox_inches='tight')
print('Overlap results saved to:', output_path + 'overlap_results.npy')
 