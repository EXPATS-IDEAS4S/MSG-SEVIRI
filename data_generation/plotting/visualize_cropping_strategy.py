import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np
import random

def plot_domain_with_orography(output_path, ds, orography_var, latmin, latmax, lonmin, lonmax, 
                               sub_latmin, sub_latmax, sub_lonmin, sub_lonmax, 
                               cropping_strategy="fixed", num_random_subdomains=3):
    """
    Plots a domain defined by lat/lon bounds and overlays orography data from a NetCDF file.
    Supports both 'fixed' and 'random' cropping strategies.

    Parameters:
        output_path (str): Path to save the output image.
        ds (xarray.Dataset): NetCDF dataset containing orography data.
        orography_var (str): Variable name for orography (e.g., "elevation").
        latmin, latmax, lonmin, lonmax (float): Bounding box for the main domain.
        sub_latmin, sub_latmax, sub_lonmin, sub_lonmax (float): Fixed subdomain (ignored if strategy is 'random').
        cropping_strategy (str): 'fixed' or 'random'.
        num_random_subdomains (int): Number of random subdomains if using 'random' strategy.
    """

    # Extract latitude, longitude, and orography data
    lats = ds['lat'].values
    lons = ds['lon'].values
    orography = ds[orography_var].values

    # Mask the sea (elevation ≤ 0)
    sea_mask = orography <= 0
    land_mask = orography > 0

    # Create the figure and set projection
    fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})

    # Plot the sea (masked in blue)
    ax.pcolormesh(lons, lats, np.where(sea_mask, np.nan, orography), cmap='terrain', shading='auto', transform=ccrs.PlateCarree())
    ax.pcolormesh(lons, lats, np.where(sea_mask, 1, np.nan), cmap='Blues', shading='auto', transform=ccrs.PlateCarree())

    # Add features
    ax.add_feature(cfeature.COASTLINE, linewidth=1)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.LAND, edgecolor='black', linewidth=0.5)
    ax.set_extent([lonmin, lonmax, latmin, latmax], crs=ccrs.PlateCarree())

    # Add colorbar for land elevation
    cbar = plt.colorbar(ax.pcolormesh(lons, lats, np.where(land_mask, orography, np.nan), cmap='terrain', shading='auto', transform=ccrs.PlateCarree()), 
                        ax=ax, orientation='vertical', shrink=0.7)
    cbar.set_label('Orography (m)')

    # Define colors for random subdomains
    subdomain_colors = ['red', 'magenta', 'cyan', 'yellow', 'lime', 'orange']

    if cropping_strategy == "fixed":
        # Highlight the fixed subdomain
        ax.plot([sub_lonmin, sub_lonmax, sub_lonmax, sub_lonmin, sub_lonmin], 
                [sub_latmin, sub_latmin, sub_latmax, sub_latmax, sub_latmin], 
                color='red', linewidth=2, transform=ccrs.PlateCarree(), label="Subdomain")
    elif cropping_strategy == "random":
        for i in range(num_random_subdomains):
            # Generate random subdomain within main domain
            sub_width = sub_lonmax - sub_lonmin
            sub_height = sub_latmax - sub_latmin

            rand_sub_lonmin = random.uniform(lonmin, lonmax - sub_width)
            rand_sub_lonmax = rand_sub_lonmin + sub_width
            rand_sub_latmin = random.uniform(latmin, latmax - sub_height)
            rand_sub_latmax = rand_sub_latmin + sub_height

            color = subdomain_colors[i % len(subdomain_colors)]  # Cycle through colors

            # Highlight the random subdomain
            ax.plot([rand_sub_lonmin, rand_sub_lonmax, rand_sub_lonmax, rand_sub_lonmin, rand_sub_lonmin], 
                    [rand_sub_latmin, rand_sub_latmin, rand_sub_latmax, rand_sub_latmax, rand_sub_latmin], 
                    color=color, linewidth=2, transform=ccrs.PlateCarree(), label=f"Subdomain {i+1}")

    # Labels and title
    ax.set_title(f"Orography Map ({cropping_strategy.capitalize()} Subdomain)")

    # Save the plot
    output_file = f"{output_path}/orography_{cropping_strategy}_subdomain_{sub_latmin}_{sub_latmax}_{sub_lonmin}_{sub_lonmax}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')

    print(f"Plot saved to: {output_file}")


dem_file = '/data1/other_data/DEM_EXPATS_0.01x0.01.nc'

run_name = 'dcv2_ir108_200x200_k9_expats_70k_200-300K_closed-CMA'

output_path = f'/data1/fig/{run_name}'

# Open the dem file
ds = xr.open_dataset(dem_file, decode_times=False, engine='h5netcdf')
print(ds)

# plot_domain_with_orography(
#     output_path=output_path,
#     ds=ds,
#     orography_var="DEM",    # Change this to match your NetCDF variable name
#     latmin=42, latmax=51.5, lonmin=5, lonmax=16, 
#     sub_latmin=42, sub_latmax=50, sub_lonmin=6.5, sub_lonmax=14.5,
#     cropping_strategy="fixed"
# )



# Random cropping strategy 
plot_domain_with_orography(
    output_path=output_path,
    ds=ds,
    orography_var="DEM",
    latmin=42, latmax=51.5, lonmin=5, lonmax=16, 
    sub_latmin=42.62, sub_latmax=47.62, sub_lonmin=8, sub_lonmax=13.2,
    cropping_strategy="fixed",
    num_random_subdomains=1
)

plot_domain_with_orography(
    output_path=output_path,
    ds=ds,
    orography_var="DEM",
    latmin=42, latmax=51.5, lonmin=5, lonmax=16, 
    sub_latmin=45.88, sub_latmax=51., sub_lonmin=10.38, sub_lonmax=15.5,
    cropping_strategy="fixed",
    num_random_subdomains=1
)
