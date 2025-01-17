import xarray as xr
import numpy as np
import pandas as pd
import glob
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.colors as mcolors
from scipy.interpolate import griddata
from datetime import datetime, timedelta
import os
from scipy.ndimage import binary_closing

# Function to apply binary closing with a square structure of given size
def apply_closing(image, size):
    structure = np.ones((size, size), dtype=np.uint8)
    closed_image = binary_closing(image, structure=structure)
    return closed_image

structure_sizes = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

# Define paths
cmsaf_folder = "/data1/crops/cmsaf_2013-2014-2015-2016_expats/nc_clouds/"
modis_folder = "/data1/other_data/MODIS/2013/"
cmsaf_files = sorted(glob.glob(f"{cmsaf_folder}2013*_EXPATS_0.nc"))
modis_files = sorted(glob.glob(f"{modis_folder}CLDMSK_L2_MODIS_Aqua*.nc"))

output_path = "/home/Daniele/fig/cma_analysis/modis/conf_matrix/"

lonmin_plot, lonmax_plot, latmin_plot, latmax_plot = 5, 16, 42, 51.5

plot = False
closing = True
if closing:
    output_path = "/home/Daniele/fig/cma_analysis/modis/conf_matrix/closing/"
    os.makedirs(output_path, exist_ok=True)

def regrid_nearest_1d(src_lat, src_lon, src_values, target_lat, target_lon):
    """
    Regrids the source data to the target grid using nearest neighbor interpolation.

    Parameters:
    - src_lat (1D array): Source latitude grid.
    - src_lon (1D array): Source longitude grid.
    - src_values (1D array): Source data to be regridded.
    - target_lat (1D array): Target latitude grid.
    - target_lon (1D array): Target longitude grid.

    Returns:
    - 1D array: Data regridded to the target grid.
    """
    # Flatten the source lat/lon grid and data
    src_points = np.column_stack((src_lat, src_lon))
    #src_values = src_data

    # Flatten the target lat/lon grid
    target_points = np.column_stack((target_lat, target_lon))

    # Perform nearest-neighbor interpolation
    regridded_data = griddata(
        points=src_points, values=src_values, xi=target_points, method='nearest'
    )

    # Reshape to match the target grid shape
    return regridded_data#.reshape(target_lat.shape)


def regrid_nearest_2d(src_lat, src_lon, src_data, target_lat, target_lon):
    """
    Regrids the source data to the target grid using nearest neighbor interpolation.

    Parameters:
    - src_lat (2D array): Source latitude grid.
    - src_lon (2D array): Source longitude grid.
    - src_data (2D array): Source data to be regridded (may contain NaNs).
    - target_lat (2D array): Target latitude grid.
    - target_lon (2D array): Target longitude grid.

    Returns:
    - 2D array: Data regridded to the target grid, preserving NaNs where necessary.
    """
    # Flatten the source arrays and remove NaN values
    valid_src_mask = ~src_lat.mask & ~src_lon.mask & ~src_data.mask
    valid_src_points = np.column_stack((src_lat[valid_src_mask], src_lon[valid_src_mask]))
    valid_src_values = src_data[valid_src_mask]
    #print(valid_src_points.shape, valid_src_values.shape)

    # Flatten the target arrays
    valid_target_mask = ~target_lat.mask & ~target_lon.mask
    target_points = np.column_stack((target_lat[valid_target_mask], target_lon[valid_target_mask]))

    # Initialize the output array with NaNs
    regridded_data = np.full(target_lat.shape, np.nan)

    # Perform nearest-neighbor interpolation only for valid target points
    interpolated_values = griddata(
        points=valid_src_points,
        values=valid_src_values,
        xi=target_points,
        method='nearest'
    )

    # Assign interpolated values to the valid locations in the output array
    regridded_data[valid_target_mask] = interpolated_values
    regridded_data = np.ma.masked_invalid(regridded_data)

    return regridded_data


def binarize_modis_mask(modis_mask):
    """
    Binarizes the MODIS cloud mask by replacing values:
    - Set to 1 for 0 and 1.
    - Set to 1 for 2 and 3.
    - Keep NaN and -1 unchanged.

    Parameters:
    - modis_mask (2D array): Input MODIS mask array.

    Returns:
    - binarized_mask (2D array): Binarized cloud mask.
    - valid_mask (2D array): Boolean mask indicating valid (non -1 and non-NaN) points.
    """
    # Create a valid mask for points that are not -1 and not NaN
    valid_mask = (modis_mask.data != -1) & (~modis_mask.mask)

    # Initialize the binarized mask with NaN
    binarized_mask = np.full_like(modis_mask, np.nan, dtype=float)
    binarized_mask[valid_mask] = np.where((modis_mask[valid_mask] <= 1), 1, 0)  # Cloudy: 1, Clear: 0
    binarized_mask = np.ma.masked_invalid(binarized_mask)

    return binarized_mask, valid_mask


def mask_domain(data, lat, lon, lonmin, lonmax, latmin, latmax):
    """
    Masks data based on a specified lat/lon domain.
    
    Parameters:
    - data (numpy.ndarray): 2D or 3D array of data to be masked.
    - lat (numpy.ndarray): 2D array of latitude values corresponding to `data`.
    - lon (numpy.ndarray): 2D array of longitude values corresponding to `data`.
    - domain (dict): Dictionary with 'latmin', 'latmax', 'lonmin', 'lonmax' as keys.

    Returns:
    - masked_data (numpy.ndarray): Data masked outside the specified domain.
    - mask (numpy.ndarray): Boolean mask indicating the valid domain area.
    """    
    # Create a boolean mask for the domain
    mask = (lat >= latmin) & (lat <= latmax) & (lon >= lonmin) & (lon <= lonmax)
    
    # Apply the mask to the data
    masked_data = np.where(mask, data, np.nan)
    
    return masked_data, mask


results = []

for modis_file in modis_files:
    with xr.open_dataset(modis_file) as modis_ds:
        modis_start_time = pd.to_datetime(modis_ds.attrs["time_coverage_start"]).tz_localize(None)
        modis_end_time = pd.to_datetime(modis_ds.attrs["time_coverage_end"]).tz_localize(None)
        print('MODIS scan times: ', modis_start_time, modis_end_time)

    # Find the closest CMSAF file based on MODIS time
    cmsaf_match = None
    for cmsaf_file in cmsaf_files:
        cmsaf_filename = os.path.basename(cmsaf_file)
        cmsaf_date_info = cmsaf_filename.split("_")[0]  # Extract '20130401'
        cmsaf_time_info = cmsaf_filename.split("_")[1]  # Extract '00:00'
        #print(cmsaf_date_info, cmsaf_time_info)

        # Combine date and time to create a datetime object
        try:
            cmsaf_start_time = datetime.strptime(f"{cmsaf_date_info}T{cmsaf_time_info}", "%Y%m%dT%H:%M")
            cmsaf_end_time = cmsaf_start_time + timedelta(minutes=15)
        except ValueError as e:
            print(f"Error parsing CMSAF file time from {cmsaf_filename}: {e}")
            continue

        #print(f'CMSAF scan times: {cmsaf_start_time} to {cmsaf_end_time}')

        # Check if MODIS scan times fall within CMSAF scan window
        if cmsaf_start_time <= modis_start_time and modis_end_time <= cmsaf_end_time:
            cmsaf_match = cmsaf_file
            print(f"Matching CMSAF file found: {cmsaf_match}")
            break

    if not cmsaf_match:
        print(f"No matching CMSAF file found for MODIS file: {modis_file}")
        continue

    # Process the matched CMSAF file
    print(f"Processing CMSAF file: {cmsaf_match}")
    with xr.open_dataset(cmsaf_match) as cmsaf_ds:
        cmsaf_cloud_mask = cmsaf_ds["cma"].values
        cmsaf_lat = cmsaf_ds["lat"].values
        cmsaf_lon = cmsaf_ds["lon"].values
        latmin_cmsaf = cmsaf_lat.min()
        latmax_cmsaf = cmsaf_lat.max()
        lonmin_cmsaf = cmsaf_lon.min()
        lonmax_cmsaf = cmsaf_lon.max()
        cmsaf_lat_grid, cmsaf_lon_grid = np.meshgrid(cmsaf_lat, cmsaf_lon, indexing="ij")

    with xr.open_dataset(modis_file, group="geophysical_data") as modis_cma_ds:
        modis_cloud_mask = modis_cma_ds["Integer_Cloud_Mask"].values
     
    with xr.open_dataset(modis_file, group="geolocation_data") as modis_geo_ds:
        modis_lat_grid = modis_geo_ds["latitude"].values
        modis_lon_grid = modis_geo_ds["longitude"].values
        print(modis_lat_grid.shape)

    #Get the cmsaf mask value that are within the overpass
    latmin_modis = modis_lat_grid.min()
    latmax_modis = modis_lat_grid.max()
    lonmin_modis = modis_lon_grid.min()
    lonmax_modis = modis_lon_grid.max()

    # Find common boundaries for CMSAf and MODIS
    latmin = max(latmin_modis, latmin_cmsaf)
    latmax = min(latmax_modis, latmax_cmsaf)
    lonmin = max(lonmin_modis, lonmin_cmsaf)
    lonmax = min(lonmax_modis, lonmax_cmsaf)

    print('Boundaries:',latmin,latmax,lonmin,lonmax)

    # Mask the MODIS data based on the common boundaries
    mask_lat_modis = (modis_lat_grid > latmin) & (modis_lat_grid < latmax)
    mask_lon_modis = (modis_lon_grid > lonmin) & (modis_lon_grid < lonmax)

    # Combine the masks to create a single mask for the domain
    combined_mask_modis = mask_lat_modis & mask_lon_modis

    # Apply the mask to retain the original 2D shape
    modis_lat_masked = np.ma.masked_where(~combined_mask_modis, modis_lat_grid)#.filled(np.nan)
    modis_lon_masked = np.ma.masked_where(~combined_mask_modis, modis_lon_grid)#.filled(np.nan)
    modis_cloud_masked = np.ma.masked_where(~combined_mask_modis, modis_cloud_mask)#.filled(np.nan)
    
    #modis_lat_masked = modis_lat_grid[mask_lat_modis & mask_lon_modis]
    #modis_lon_masked = modis_lon_grid[mask_lat_modis & mask_lon_modis]
    #modis_cloud_masked = modis_cloud_mask[mask_lat_modis & mask_lon_modis]
    #print(modis_lat_masked.shape, modis_lon_masked.shape, modis_cloud_masked.shape)

    tot_cmsaf_points = len(cmsaf_cloud_mask.ravel())
    if np.sum(~modis_cloud_masked.mask)<tot_cmsaf_points*0.5:
        print('not enough point to regrid')
        continue

    for structure in structure_sizes:
        #Apply closing algorithm
        cmsaf_cloud_mask = apply_closing(cmsaf_cloud_mask, structure)

        # Mask the CMSAF data based on the common boundaries
        mask_lat_cmsaf = (cmsaf_lat_grid > latmin) & (cmsaf_lat_grid < latmax)
        mask_lon_cmsaf = (cmsaf_lon_grid > lonmin) & (cmsaf_lon_grid < lonmax)
        
        # Combine the masks to create a single mask for the domain
        combined_mask_cmsaf = mask_lat_cmsaf & mask_lon_cmsaf

        # Apply the mask to retain the original 2D shape
        cmsaf_lat_masked = np.ma.masked_where(~combined_mask_cmsaf, cmsaf_lat_grid)#.filled(np.nan)
        cmsaf_lon_masked = np.ma.masked_where(~combined_mask_cmsaf, cmsaf_lon_grid)#.filled(np.nan)
        #cmsaf_lat_masked = cmsaf_lat_grid[mask_lat_cmsaf & mask_lon_cmsaf]
        #cmsaf_lon_masked = cmsaf_lon_grid[mask_lat_cmsaf & mask_lon_cmsaf]

        # Mask the CMSAF cloud mask based on the common boundaries
        #cmsaf_cloud_masked = cmsaf_cloud_mask[mask_lat_cmsaf & mask_lon_cmsaf]
        cmsaf_cloud_masked = np.ma.masked_where(~combined_mask_cmsaf, cmsaf_cloud_mask)#.filled(np.nan)
        #print(cmsaf_cloud_masked)

        
        # Regrid CMSAF cloud mask to MODIS grid
        cmsaf_regridded = regrid_nearest_2d(cmsaf_lat_masked, cmsaf_lon_masked, cmsaf_cloud_masked, modis_lat_masked, modis_lon_masked)
        #print(cmsaf_regridded)
        #print(modis_lon_masked.shape, modis_lat_masked.shape)

        # Binarize MODIS cloud mask and apply the same mask to CMSAF
        #print(np.sum(modis_cloud_masked==0)+np.sum(modis_cloud_masked==1))
        #print(np.sum(modis_cloud_masked==2)+np.sum(modis_cloud_masked==3))
        binarized_modis_mask, valid_mask = binarize_modis_mask(modis_cloud_masked)
        #binarized_modis_mask = np.ma.masked_where(~valid_mask, binarized_modis_mask).filled(np.nan)
        #print(np.sum(binarized_modis_mask==0), np.sum(binarized_modis_mask==1))

    
        cmsaf_regridded = np.ma.masked_where(~valid_mask, cmsaf_regridded)#.filled(np.nan)
        modis_lat_masked = np.ma.masked_where(~valid_mask, modis_lat_masked)#.filled(np.nan)
        modis_lon_masked = np.ma.masked_where(~valid_mask, modis_lon_masked)#.filled(np.nan)
        
        # cmsaf_regridded = cmsaf_regridded[valid_mask]
        # binarized_modis_mask = binarized_modis_mask[valid_mask]
        # modis_lat_masked = modis_lat_masked[valid_mask]
        # modis_lon_masked = modis_lon_masked[valid_mask]
        # print(cmsaf_regridded.shape, binarized_modis_mask.shape)

        # Compute confusion matrix (ensure valid comparison by ignoring NaN)
        valid_mask = ~binarized_modis_mask.mask & ~cmsaf_regridded.mask
        #print(valid_mask)
        flat_binarized = binarized_modis_mask[valid_mask].ravel()
        flat_cmsaf = cmsaf_regridded[valid_mask].ravel()
        cm = confusion_matrix(flat_binarized, flat_cmsaf, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()
        tot_points = tn+fp+fn+tp

        # Store results
        results.append({
            "MODIS File": modis_file,
            "CMSAF File": cmsaf_match,
            "Closing Structure": structure,
            "True Negatives": tn,
            "False Positives": fp,
            "False Negatives": fn,
            "True Positives": tp
        })

        if plot:

            # Create an agreement map in the original 2D shape
            agreement = np.full_like(binarized_modis_mask, fill_value=np.nan, dtype=float)  # Use NaN as the default value
            agreement[(cmsaf_regridded == 1) & (binarized_modis_mask == 1)] = 0  # True Positive (TP)
            agreement[(cmsaf_regridded == 0) & (binarized_modis_mask == 0)] = 1  # True Negative (TN)
            agreement[(cmsaf_regridded == 0) & (binarized_modis_mask == 1)] = 2  # False Negative (FN)
            agreement[(cmsaf_regridded == 1) & (binarized_modis_mask == 0)] = 3  # False Positive (FP)
            agreement = np.ma.masked_invalid(agreement)
            #print(tn, np.sum(agreement==2))
            #print(fp, np.sum(agreement==4))
            #print(fn, np.sum(agreement==3))
            #print(tp, np.sum(agreement==1))
            
            # Plot the original, the masked and the regridded cmsaf cloud mask and the confusion matrix

            # Define a custom colormap with meaningful colors
            cmap = mcolors.ListedColormap(['black', 'white'])
            norm = mcolors.BoundaryNorm(boundaries=[0, 1, 2], ncolors=2)

            # Define a custom colormap with meaningful colors for confusion matrix
            cmap_cm = mcolors.ListedColormap(['blue', 'green', 'yellow', 'red'])
            norm_cm = mcolors.BoundaryNorm(boundaries=[0, 1, 2, 3, 4], ncolors=4)

            # Create a figure with 3 subplots in one row
            fig, axes = plt.subplots(1, 1, subplot_kw={'projection': ccrs.PlateCarree()}, figsize=(6, 6))

            #axes = axes.flatten()

            # Titles for the subplots
            # titles = [
            #     f"Original CMSAF CMA",
            #     f"MODIS CMA",
            #     f"CMSAF Regrid to MODIS",
            #     f'Confusion Matrix'
            # ]

            # axes[0].pcolormesh(
            #         cmsaf_lon_grid, cmsaf_lat_grid, cmsaf_cloud_mask, cmap=cmap, norm=norm, transform=ccrs.PlateCarree()
            #     )
            # im2 = axes[1].pcolormesh(
            #     modis_lon_masked, modis_lat_masked, binarized_modis_mask, cmap=cmap, norm=norm, transform=ccrs.PlateCarree()
            # )
            # axes[2].pcolormesh(modis_lon_masked, modis_lat_masked, cmsaf_regridded, cmap=cmap, norm=norm, transform=ccrs.PlateCarree() )

            im = axes.pcolormesh(
                modis_lon_masked, modis_lat_masked, agreement,
                cmap=cmap_cm, norm=norm_cm, transform=ccrs.PlateCarree()
            )

            # Add a colorbar with labels for each category
            cbar = plt.colorbar(im, ax=axes, orientation='vertical', shrink=0.6, pad=0.05)
            cbar.set_ticks([0.5, 1.5, 2.5, 3.5])
            cbar.set_ticklabels(['TP', 'TN', 'FN', 'FP'])

            # # Add a colorbar with labels for each category
            # cbar = plt.colorbar(im2, ax=axes[1], orientation='vertical', shrink=0.6, pad=0.05)
            # cbar.set_ticks([0.5, 1.5])
            # cbar.set_ticklabels(['Clear', 'Cloudy'])
            
            #for i, ax in enumerate(axes):
            # Set the extend
            axes.set_extent([lonmin_plot, lonmax_plot, latmin_plot, latmax_plot], crs=ccrs.PlateCarree())

            # Add coastlines, borders, and other features
            axes.coastlines(resolution='10m', linewidth=0.8)
            axes.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
            axes.add_feature(cfeature.LAND, facecolor='lightgray', edgecolor='black')
            axes.add_feature(cfeature.OCEAN, facecolor='lightblue')
            
            # Set the title for each subplot, with the cf values (only 2 decimals)
            axes.set_title(f"{cmsaf_start_time} - {str(cmsaf_end_time).split(' ')[1]}, closing structure {structure}x{structure} \n TP: {tp/tot_points:.2f}, TN: {tn/tot_points:.2f}, FN: {fn/tot_points:.2f}, FP: {fp/tot_points:.2f}", fontsize=11, fontweight='bold')

            # Save the entire figure
            plt.subplots_adjust(wspace=0.3)
            fig.savefig(f"{output_path}cmsaf_modis_CF_{modis_start_time:%Y%m%d%H%M}_closing_{structure}.png", bbox_inches='tight')
            plt.close()
            print('fig saved in', f"{output_path}cmsaf_modis_CF_{modis_start_time:%Y%m%d%H%M}_closing_{structure}.png")
    
# Save confusion matrix results to a DataFrame
results_df = pd.DataFrame(results)
results_df.to_csv(f"{output_path}confusion_matrix_results_closing.csv", index=False)

#nohup 2304813