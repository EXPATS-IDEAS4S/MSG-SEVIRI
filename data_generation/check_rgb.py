import rasterio 
import matplotlib.pyplot as plt

def read_and_display_tiff(file_path, plot=False):
    # Open the TIFF file using rasterio
    with rasterio.open(file_path) as src:
        # Get metadata of the image
        metadata = src.meta
        print("Metadata:", metadata)
    
        #If the image has more than one band, read them as needed
        #Example: for RGB image with 3 bands
        band1 = src.read(1)
        band2 = src.read(2)
        band3 = src.read(3)
        print(band1)
        print(band2)
        print(band3)
        
        if plot:
            # Display the image using matplotlib
            plt.figure(figsize=(10, 10))
            plt.imshow(band1, cmap='gray')  # Use 'gray' colormap for single-band images
            plt.title("TIFF Image")
            plt.axis('off')  # Hide axis
            plt.show()


# checck one file
image_dir = '/data/sat/msg/ml_train_crops/IR_108_2013_128x128_EXPATS/'
file_name = '20130401_00:00_EXPATS_0_spectral.tif'
read_and_display_tiff(image_dir+file_name)

