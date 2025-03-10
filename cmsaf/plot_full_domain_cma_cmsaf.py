import os
import glob
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from glob import glob
import numpy as np
import matplotlib.colors as mcolors

# Path to the folder containing NetCDF files
year = 2022
folder_path = f"/data/sat/msg/CM_SAF/merged_cloud_properties/{year}/04"
file_list = sorted(glob(os.path.join(folder_path, "*.nc")))
output_path = f"/home/dcorradi/Documents/Fig/gif_cma/{year}/"
# Create the output folder if it does not exist
os.makedirs(output_path, exist_ok=True)

# # Define a custom colormap with meaningful colors
# cmap = mcolors.ListedColormap(['black', 'white'])
# norm = mcolors.BoundaryNorm(boundaries=[0, 1, 2], ncolors=2)

# # Loop through each file
# for file in file_list:
#     print(f"Processing file: {file}")
    
#     # Open the NetCDF file
#     with xr.open_dataset(file) as ds:
#         # Access the `cma` variable
#         #cma = ds['cma'].values
#         lat = ds['lat'].values
#         lon = ds['lon'].values
#         #create grid
#         lat_grid, lon_grid = np.meshgrid(lat, lon, indexing='ij')
#         # get the time values
#         times = ds['time'].values

#         for i,time in enumerate(times):
#             print(time)
#             cma = ds['cma'].values[i,:,:]
#             #extract the values in ds for this time

#             # Create the plot
#             plt.figure(figsize=(6, 6))
#             ax = plt.axes(projection=ccrs.PlateCarree())
#             ax.coastlines(resolution='50m', color='red', linewidth=0.8, linestyle=':')
#             ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.8, edgecolor='red')
#             ax.add_feature(cfeature.LAND, linestyle=':', edgecolor='red', facecolor='lightgray')
#             ax.add_feature(cfeature.OCEAN, facecolor='white')

#             # Plot the data
#             cma_plot = plt.pcolormesh(lon, lat, cma, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())

#             # Add a colorbar with labels for each category
#             cbar = plt.colorbar(cma_plot, ax=ax, orientation='vertical', shrink=0.6, pad=0.05)
#             cbar.set_ticks([0.5, 1.5])
#             cbar.set_ticklabels(['Clear', 'Cloudy'])
            
#             # Add title and labels
#             ax.set_title(f"{str(time).split('.')[0]}", fontsize=14, fontweight='bold')

#             # Save the plot
#             plt.savefig(f"{output_path}cma_{time}.png", dpi=300, bbox_inches='tight')

            
        
# create gif

import os
from PIL import Image

def create_gif(image_folder, output_path, duration=500):
    """
    Create a GIF from images stored in a folder.
    
    :param image_folder: Path to the folder containing images.
    :param output_path: File path to save the GIF.
    :param duration: Time between frames in milliseconds.
    """
    # Get a sorted list of image file paths
    images = sorted(
        [os.path.join(image_folder, img) for img in os.listdir(image_folder) if img.lower().endswith(('png', 'jpg', 'jpeg'))]
    )
    
    # Check if there are images in the folder
    if not images:
        print("No images found in the folder!")
        return

    # Open images
    frames = [Image.open(image) for image in images]

    # Create GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )
    print(f"GIF saved at {output_path}")

# Specify folder and output file
#image_folder ="/home/dcorradi/Documents/Fig/gif_cma/"  # Change to your folder path
output_gif = f"{output_path}/cma_{year}.gif"  # Change to your desired output path
# Create the output folder if it does not exist
#os.makedirs(output_gif, exist_ok=True)

# Call the function to create GIF
create_gif(output_path, output_gif, duration=500)
