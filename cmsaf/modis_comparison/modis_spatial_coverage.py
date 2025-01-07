import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from glob import glob

# Paths
modis_cma_path = '/data1/other_data/MODIS/2013/'
modis_filename = 'CLDMSK_L2_MODIS_Aqua*.nc'
output_path = '/home/Daniele/fig/cma_analysis/modis/'

filepattern = modis_cma_path + modis_filename
filelist = sorted(glob(filepattern))
print(f"Found {len(filelist)} files")

# Domain boundaries
lon_min, lon_max = 5, 16  
lat_min, lat_max = 42, 51.5   

# Initialize a list to store pixel counts
pixel_counts = []

for file_path in filelist:
    print(f"Processing file: {file_path}")
    
    # Open geolocation data
    geo_ds = xr.open_dataset(file_path, group="geolocation_data")
    latitude = geo_ds['latitude'].values
    longitude = geo_ds['longitude'].values

    # Mask for pixels within the specified boundaries
    mask = (
        (longitude >= lon_min) & (longitude <= lon_max) &
        (latitude >= lat_min) & (latitude <= lat_max)
    )
    count_within_domain = np.sum(mask)
    pixel_counts.append(count_within_domain)

# Normalize pixel counts by the maximum count
normalized_counts = np.array(pixel_counts) / max(pixel_counts)
print('max pixel count: ',max(pixel_counts))
print('min pixel count: ',min(pixel_counts))	
print('mean pixel count: ',np.mean(normalized_counts))
print('sum of pixel count: ',sum(pixel_counts))
exit()
#decide the number of bins
bin_width = 0.05
bins = np.arange(0, 1 + bin_width, bin_width)

# Plot a histogram of normalized counts
plt.figure(figsize=(7, 5))
plt.hist(normalized_counts, bins=bins, color='blue', alpha=0.7, edgecolor='black')
plt.title("Distribution of Normalized Pixel Counts", fontsize=14, fontweight='bold')
plt.xlabel("Normalized Pixel Count", fontsize=12)
plt.ylabel("Frequency", fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{output_path}normalized_pixel_count_distribution.png")


