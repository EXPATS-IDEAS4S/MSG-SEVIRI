import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import xarray as xr
import matplotlib.colors as colors
import sys


sys.path.append('/home/dcorradi/Documents/Codes/NIMROD/')
from figures.plot_functions import set_map_plot

def plot_ci(data, lat, lon, time, title, extent, cmap, norm, legend_labels, domain, save=None):
    """
    Plots CI.
    Adds geographical features for context, and optionally saves the plot to a file.

    Parameters:
    - data (numpy.ndarray): 2D array of cloud mask data (0 for clear, 1 for cloudy).
    - lat (numpy.ndarray): 2D array of latitude values.
    - lon (numpy.ndarray): 2D array of longitude values.
    - time (datetime or str): Time corresponding to the data snapshot.
    - title (str): Title for the plot.
    - extent (list): Geographical extent [west, east, south, north] for the plot.
    - save (str, optional): Path to save the plot image. If None, the plot is not saved.
    """
    fig, axs = plt.subplots(figsize=(18, 5), ncols=3, subplot_kw={'projection': ccrs.PlateCarree()})
    
    for i, ax in enumerate(axs):
        # Assuming data, lat, lon, time, and title are now lists of length 3
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        mesh = ax.pcolormesh(lon, lat, data[title[i]].values, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())
        
        set_map_plot(ax, norm, cmap, extent, title[i], '', False)
        
        if i == len(axs) - 1:  # Adding legend to the last plot
            ax.legend(handles=legend_labels, loc='lower right', title="CI PROB")

    # Set an overall title for the figure
    fig.suptitle('Convection Iniziation Probability - '+str(time), fontsize=16, fontweight='bold')

    # Adjust the spacing at the top of the figure to make room for the overall title
    fig.subplots_adjust(top=0.9)

    # Save the plot
    if save:
        date_string = str(time)#.strftime('%Y-%m-%d %H:%M')
        plot_filename = save+'maps_'+domain+'/CI_'+date_string.replace(' ','_')+'.png'
        savefile(fig,plot_filename)


def savefile(fig,plot_filename):
    fig.savefig(plot_filename, dpi=300, bbox_inches='tight')
    print(f"Plot saved as {plot_filename}")
    plt.close()




def plot_ci_flag_distribution(ci_status_flag, flag_values, flag_meanings, flag_name, save):
    """
    Plots the normalized distribution of CI flags.

    Parameters:
    - ci_status_flag (numpy.ndarray): 2D array of CI status flags.
    - flag_values (list): List of individual flag values.
    - flag_meanings (list): Descriptions corresponding to each flag value.
    """
    # Ensure ci_status_flag is of integer type
    ci_status_flag = ci_status_flag.astype(int)

    # Initialize a dictionary to count occurrences of each flag
    flag_counts = {val: 0 for val in flag_values}

    # Iterate over each flag value to count its occurrences
    for val in flag_values:
        #print(val)
        mask = np.bitwise_and(ci_status_flag, val) == val
        flag_counts[val] = np.sum(mask)

    # Calculate the total number of points for normalization
    total_points = len(ci_status_flag)
    print(total_points)

    # Prepare data for plotting
    labels = flag_meanings
    
    # Normalize counts by dividing by the total number of points
    normalized_counts = [flag_counts[val] / total_points for val in flag_values]
    print(normalized_counts)

    # Plotting
    fig, ax = plt.subplots()
    ax.bar(labels, normalized_counts)
    #ax.set_xlabel('Flag Meaning')
    ax.set_ylabel('Normalized Count')
    ax.set_title(flag_name.replace('_',' ')+' flag')
    plt.xticks(rotation=45, ha="right")

    plot_filename = save+flag_name+'_flag_distr.png'
    savefile(fig,plot_filename)



def compute_normalized_count(ds, var_names):
    """
    Computes the normalized count of occurrences of the value 4 for given variables
    over the time dimension, across all lat-lon points, for each variable in var_names.

    Parameters:
    - ds (xarray.Dataset): The input dataset.
    - var_names (list of str): The names of the variables to analyze.

    Returns:
    - xarray.Dataset: A dataset of normalized counts for each variable at each lat-lon grid point.
    """
    
    # Initialize an empty dataset to store the results
    result_ds = xr.Dataset()
    
    for var_name in var_names:
        # Check if the variable exists in the dataset
        if var_name not in ds.variables:
            raise ValueError(f"The variable {var_name} is not in the dataset.")
        
        # Extract the variable of interest
        var_data = ds[var_name]
        
        # Count occurrences where the variable equals 4, along the time dimension
        count_4 = (var_data == 4).sum(dim='time')
        
        # Calculate the total number of time steps
        #total_time_steps = ds.dims['time']
        
        # Normalize the counts by the total number of time steps
        #normalized_count = count_4 / total_time_steps
        
        # Add the normalized count to the result dataset
        result_ds[var_name] = count_4
    
    return result_ds


def plot_ci_count(ds_oro,ds_data, lat, lon, title, extent, cmap, domain, save=None):
    """
    Plots CI.
    Adds geographical features for context, and optionally saves the plot to a file.

    Parameters:
    - data (numpy.ndarray): 2D array of cloud mask data (0 for clear, 1 for cloudy).
    - lat (numpy.ndarray): 2D array of latitude values.
    - lon (numpy.ndarray): 2D array of longitude values.
    - time (datetime or str): Time corresponding to the data snapshot.
    - title (str): Title for the plot.
    - extent (list): Geographical extent [west, east, south, north] for the plot.
    - save (str, optional): Path to save the plot image. If None, the plot is not saved.
    """
    fig, axs = plt.subplots(figsize=(18, 5), ncols=3, subplot_kw={'projection': ccrs.PlateCarree()})
    vmin, vmax = find_overall_max_min(ds_data, title)
    norm = colors.Normalize(vmin=vmin, vmax=vmax)
    for i, ax in enumerate(axs):
        # Orography as background (in grayscale)
        ax.pcolormesh(ds_oro['lons'].values,ds_oro['lats'].values,ds_oro['orography'].values,cmap='Greys', alpha=0.5, transform=ccrs.PlateCarree())

        # Copy the data to modify values of 0 to NaN
        data = ds_data[title[i]].where(ds_data[title[i]] != 0)

        # Assuming data, lat, lon, time, and title are now lists of length 3
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        mesh = ax.pcolormesh(lon, lat, data.values, cmap=cmap, norm=norm, transform=ccrs.PlateCarree())

        set_map_plot(ax, norm, cmap, extent, title[i], 'Probability', False)

    # Adjust layout to make room for the colorbar
    plt.subplots_adjust(right=0.80)
    
    # Add colorbar to the right of the last subplot
    cbar_ax = fig.add_axes([0.85, 0.20, 0.01, 0.6])  # Adjust the dimensions as needed [left, bottom, width, height]
    cbar = fig.colorbar(mesh, cax=cbar_ax, orientation='vertical')
    cbar.set_label('Counts', rotation=270, labelpad=15)
    
    # Set an overall title for the figure
    fig.suptitle('Convection Iniziation Probability 75-100%', fontsize=16, fontweight='bold')

    # Adjust the spacing at the top of the figure to make room for the overall title
    fig.subplots_adjust(top=0.9)

    # Save the plot
    if save:
        plot_filename = save+'CI_count_above75_'+domain+'.png'
        savefile(fig,plot_filename)


def find_overall_max_min(ds, var_names):
    """
    Find the overall maximum and minimum values across specified variables in a Dataset.
    
    Parameters:
    - ds (xarray.Dataset): The input dataset.
    - var_names (list of str): Names of the variables to include in the analysis.
    
    Returns:
    - (float, float): A tuple containing the overall maximum and minimum values.
    """
    max_vals = []
    min_vals = []
    
    for var_name in var_names:
        # Ensure the variable is in the dataset
        if var_name in ds:
            max_vals.append(ds[var_name].max().values)
            min_vals.append(ds[var_name].min().values)
        else:
            print(f"Warning: Variable '{var_name}' not found in the dataset.")
    
    overall_max = max(max_vals) if max_vals else None
    overall_min = min(min_vals) if min_vals else None
    
    return overall_min, overall_max