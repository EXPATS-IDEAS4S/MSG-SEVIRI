import rasterio 
import matplotlib.pyplot as plt
from glob import glob
import numpy as np

def read_and_display_tiff(file_path, print_metadata=False, plot=False, colormode='RGB'):
    # Open the TIFF file using rasterio
    with rasterio.open(file_path) as src:
        # Get metadata of the image
        if print_metadata:
            metadata = src.meta
            print("Metadata:", metadata)
    
        #If the image has more than one band, read them as needed
        #Example: for RGB image with 3 bands
        band1 = src.read(1)
        if colormode == 'RGB':
            band2 = src.read(2)
            band3 = src.read(3)
        #print(band1)
        #print(band2)
        #print(band3)
        
        if plot:
            # Display the image using matplotlib
            plt.figure(figsize=(10, 10))
            plt.imshow(band1, cmap='gray')  # Use 'gray' colormap for single-band images
            plt.title("TIFF Image")
            plt.axis('off')  # Hide axis
            plt.show()

        return band1, band2, band3



def plot_distribution_of_crops(crop_file_paths, bins, norm_type, out_path):  
    """
    Plots the distribution of values from a specified band of multiple TIFF crops.

    :param crop_file_paths: list of str
        List of file paths to the TIFF crops.
    :param band_index: int
        The band index to extract values from (1-based index). Default is 1 (the first band).
    :param bins: int
        The number of bins to use for the histogram. Default is 50.
    
    :return: None
    """

    # List to hold all values from the specified band
    all_band_values = []

    # Iterate over each crop file path
    for file_path in crop_file_paths:
        print(file_path.split('/')[-1])
        # Extract the first band and flatten it
        band_values = read_and_display_tiff(file_path)[0].flatten()
    
        # Append to the list
        all_band_values.append(band_values)

    # Concatenate all the arrays into one plain array
    all_band_values = np.concatenate(all_band_values)

    # Plot the histogram of the values
    fig, axes = plt.subplots(figsize=(10, 6))
    plt.hist(all_band_values, bins=bins, color='skyblue', log=True)
    plt.title(f'Distribution of one band of RGB crops - {norm_type}')
    plt.xlabel('Pixel Value of Colormap')
    plt.ylabel('Counts (log scale)')
    plt.grid(True)
    fig.savefig(f'{out_path}distribution_rgb_{norm_type}.png', bbox_inches='tight')



norm_type = '10th-90th'
color_mode = 'greyscale'

# checck one file
image_dir = f'/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/tif_{norm_type}_{color_mode}/'
file_name = f'20130402_01:00_EXPATS_0_{norm_type}_{color_mode}.tif'
band1 = read_and_display_tiff(image_dir+file_name, print_metadata=True)[0]
print(band1)

# # Open all crops
# crop_list = sorted(glob(image_dir+'*tif'))


# bins =  np.arange(0, 255 + 2, 2)

# plot_distribution_of_crops(crop_list, bins, norm_type, image_dir )

