import os
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr
import pandas as pd  # Import pandas

# Paths
vis_folder_path = "/data/sat/msg/netcdf/parallax/2013/04"
cma_folder_path = "/data/sat/msg/CM_SAF/CMA_processed/2013/04"
output_path = "/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/VIS_images/"

# Create output directory if it doesn't exist
os.makedirs(output_path, exist_ok=True)

# Define the time range for day (08:00 - 16:00)
start_hour = 8
end_hour = 16

# Loop over each file in the VIS folder
vis_file = os.path.join(vis_folder_path, '20130401-EXPATS-RG.nc')  # Change to the specific file
vis_ds = xr.open_dataset(vis_file)

# Extract the `VIS006` variable
vis_data = vis_ds['VIS006']
times = sorted(vis_ds.coords['time'].values)

# Set up Cartopy projection
projection = ccrs.PlateCarree()

# Loop through the times and create plots for hours between 08:00 and 16:00
for time in times:
    # Convert numpy.datetime64 to pandas.Timestamp for easier manipulation
    time_dt = pd.to_datetime(time)
    print(time_dt)

    # Check if the hour is within the 08:00 - 16:00 range
    if time_dt.hour < start_hour or time_dt.hour > end_hour:
        continue  # Skip times outside of the 08:00 - 16:00 range

    # Find the corresponding day folder in the CMA data folder
    #select the day with DD format
    day_str = str(time_dt.day)#.strftime('%Y%m%d').day  # Example: "20130430"
    # COvnert the string to 'dd' format
    day_str = day_str.zfill(2)
    cma_day_folder = os.path.join(cma_folder_path, day_str)
    
    if not os.path.exists(cma_day_folder):
        print(f"Folder not found: {cma_day_folder}")
        continue

    # Find the correct CMA file for the given time
    cma_filename = f"CMAin{time_dt.strftime('%Y%m%d%H%M%S')}405SVMSG01UD.nc"
    print(cma_filename)
    cma_file = os.path.join(cma_day_folder, cma_filename)

    if not os.path.exists(cma_file):
        print(f"File not found: {cma_file}")
        continue
    
    # Open the CMA dataset and extract the cloud mask (cma)
    cma_ds = xr.open_dataset(cma_file)
    cma_data = cma_ds['cma']

    # Set up the figure with two subplots
    fig, axes = plt.subplots(1, 2, figsize=(12, 6), subplot_kw={'projection': projection})

    # Plot VIS006 data
    ax = axes[0]
    vis_values = vis_data.sel(time=time)  # Extract the data for the current time
    ax.set_extent([vis_ds.lon.min(), vis_ds.lon.max(), vis_ds.lat.min(), vis_ds.lat.max()], crs=projection)
    im = ax.pcolormesh(vis_ds.lon, vis_ds.lat, vis_values, cmap='gray', shading='auto', transform=projection)
    ax.coastlines()
    ax.set_title(f'VIS006 for {time_dt}')
    fig.colorbar(im, ax=ax, orientation='vertical', label='VIS006', pad=0.05, shrink=0.7)

    # Plot cma data
    ax = axes[1]
    cma_values = cma_data.sel(time=time)  # Extract the cloud mask data for the current time
    ax.set_extent([cma_ds.lon.min(), cma_ds.lon.max(), cma_ds.lat.min(), cma_ds.lat.max()], crs=projection)
    im = ax.pcolormesh(cma_ds.lon, cma_ds.lat, cma_values, cmap='gray', vmin=0, vmax=1, shading='auto', transform=projection)
    ax.coastlines()
    ax.set_title(f'Cloud Mask for {time_dt}')
    # Add colorbar with labels "Clear" for 0 and "Cloudy" for 1
    cbar = fig.colorbar(im, ax=ax, orientation='vertical', pad=0.05, shrink=0.7)
    cbar.set_ticks([0, 1])  # Only show 0 and 1 on the colorbar
    cbar.set_ticklabels(['Clear', 'Cloudy'])  # Label the ticks as 'Clear' and 'Cloudy'
    cbar.set_label('Cloud Mask', rotation=270, labelpad=15)  # Set label for the colorbar

    # Save the plot
    plt.tight_layout()
    plot_filename = os.path.join(output_path, f"VIS_CMA_{time_dt.strftime('%Y%m%d%H%M%S')}.png")
    plt.savefig(plot_filename)
    plt.close()

    print(f"Saved plot for {time_dt}")

