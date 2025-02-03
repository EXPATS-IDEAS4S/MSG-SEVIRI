import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def plot_ir108_from_nc(file_path):
    """
    Reads a NetCDF file and plots the 'IR_108' variable using Cartopy.

    :param file_path: str
        Path to the NetCDF file to be read and plotted.
    """
    # Open the NetCDF file
    ds = xr.open_dataset(file_path)
    print(ds)
    
    # Extract the 'IR_108' variable
    ir108 = ds['IR_108']

    time = ds['time'].values[0]
    
    # Extract latitude and longitude
    lats = ds['lat'].values
    lons = ds['lon'].values

    # Create a figure and Cartopy plot
    fig, ax = plt.subplots(
        figsize=(8, 8),
        subplot_kw={'projection': ccrs.PlateCarree()}
    )
    
    # Plot the data with a gray colormap
    im = ax.pcolormesh(lons, lats, ir108.values.squeeze(), cmap='gray_r', shading='auto', transform=ccrs.PlateCarree())
    
    # Add coastlines, borders, and gridlines
    ax.coastlines(resolution='10m', linewidth=1, color='yellow')
    ax.add_feature(cfeature.BORDERS, linewidth=1, color='yellow')
    #ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)

    # Add a colorbar
    cbar = fig.colorbar(im, ax=ax, orientation='vertical', shrink=0.7, pad=0.05)
    cbar.set_label('IR_108 BT (K)', fontsize=12)

    # Add a title
    ax.set_title('IR_108 Data from {}'.format(file_path.split('/')[-1]), fontsize=14)
    
    # Show the plot
    plt.savefig(f'{output_path}ir108_{time}.png', dpi=300, bbox_inches='tight')

# Example usage
file_path = '/work/dcorradi/crops/IR_108_2013_200x200_EXPATS_fixed/nc/20130401_00:00_EXPATS_0.nc'
output_path = '/work/dcorradi/crops/IR_108_2013_200x200_EXPATS_fixed/png/'
plot_ir108_from_nc(file_path)
