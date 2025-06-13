import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def plot_colorbar(vmin, vmax, colormap_name, out_dir, title='', unit='',  ticks=None):
    """
    Plot a colorbar with the specified colormap, value range, title, and unit.

    Parameters:
    vmin (float): The minimum value of the scale.
    vmax (float): The maximum value of the scale.
    colormap_name (str): The name of the colormap to use.
    title (str): The title of the colorbar.
    unit (str): The unit of the colorbar values.
    """
    # Create a colormap instance
    colormap = plt.get_cmap(colormap_name)

    # Normalize the color scale
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    # Create a scalar mappable object
    scalar_mappable = plt.cm.ScalarMappable(norm=norm, cmap=colormap)

    # Plot the colorbar
    fig, ax = plt.subplots(figsize=(1, 12))
    cbar = fig.colorbar(scalar_mappable, cax=ax, orientation='vertical', ticks=ticks)

    # Set the colorbar title and unit
    cbar.set_label(f'{title} [{unit}]', fontweight='bold', fontsize=12)

    # Ensure ticks and tick labels are displayed
    if ticks is not None:
        cbar.set_ticks(ticks)
        cbar.set_ticklabels([f'{tick:.2f}' for tick in ticks])

    # Disable the main axis frame and labels, but keep the ticks
    ax.set_frame_on(False)
    ax.xaxis.set_tick_params(size=0)

    fig.savefig(f'{out_dir}colorbar_{title}.png',  bbox_inches='tight')

data_dir = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/'

#open max and min
vmin , vmax = np.load(data_dir+'global_min_max.npy')

print(vmin, vmax)
#Computed global min: 202.13882446289062 and global max: 313.4286193847656

#create ticks
ticks = np.arange(vmin, vmax, 10)

plot_colorbar(vmin, vmax,'Spectral', data_dir, title='IR_108 Brightness Temperature', unit='K', ticks= ticks)
