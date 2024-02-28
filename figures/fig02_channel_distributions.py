"""
code to derive spectral features useful for detecting deep convection
and precipitation, based on master thesis of Claudia

"""
from readers.msg_ncdf import read_ncdf, ch_list, ch_max_list, ch_min_list
from readers.files_dirs import path_dir_tree, path_figs
import numpy as np
import matplotlib.pyplot as plt
import os

def main():

    # read data of the month of july
    yy = '2023'
    mm = '07'
    

    # derive distribution of values
    for i, ch in enumerate(ch_list):
        
        print('processing '+ch)

        # reading input files
        data = read_ncdf(path_dir_tree+'/'+yy+'/'+mm+'/', ch)
        
        # reading channel variable 
        channel = data[ch].values.flatten()
 
        # call plotting of channel distributions
        ch_min = ch_min_list[i]
        ch_max = ch_max_list[i]
        
        # plot distribution of values for the selected channel
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

    return

if __name__ == "__main__":
    main()
        