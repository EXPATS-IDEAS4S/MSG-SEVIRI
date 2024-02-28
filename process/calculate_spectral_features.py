"""
code to derive spectral features useful for detecting deep convection
and precipitation, based on master thesis of Claudia

"""
from readers.msg_ncdf import read_ncdf, ch_list
from readers.files_dirs import path_dir_tree, path_figs
import numpy as np
import matplotlib.pyplot as plt
import os

def main():

    # read data of the month of july
    yy = '2023'
    mm = '07'
    
    # reading input files
    data = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', "IR_108")
    
    
    # derive distribution of values
    for i, ch in enumerate(ch_list):
        # reading channel variable 
        channel = data[ch].values.flatten()
        # call plotting of channel distributions
        ch_min = np.nanmin(channel)
        ch_max = np.nanmax(channel)
        plot_distribution_channel(channel, ch, ch_min, ch_max, path_figs)
    
    
def plot_distribution_channel(channel, ch_name, ch_min, ch_max, path_out):
    """
    plot distribution of a single channel
    """   

    fig, ax= plt.subplots(figsize=(8,8))
    ax.spines["top"].set_linewidth(3)
    ax.spines["right"].set_linewidth(3)
    ax.spines["bottom"].set_linewidth(3)
    ax.spines["left"].set_linewidth(3)
    
    ax.hist(channel, 
            range=[ch_min, ch_max], 
            density=True, 
            histtype='step', 
            linewidth=4)
    

    ax.set_xlabel(ch_name)
    ax.set_ylabel('Norm occ []')
    ax.tick_params(which='minor', length=5, width=2)
    ax.tick_params(which='major', length=7, width=3)

    plt.savefig(
        os.path.join(path_out, ch_name+"_july_2023.png"),
        dpi=300,
        bbox_inches="tight",
        transparent=True,
        )


if __name__ == "__main__":
    main()
        