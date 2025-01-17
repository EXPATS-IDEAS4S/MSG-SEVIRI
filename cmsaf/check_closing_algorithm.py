import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import binary_closing
import rasterio
from glob import glob

# Function to binarize the image
def binarize_image(image):
    return (image > 0).astype(np.uint8)

# Function to apply binary closing with a square structure of given size
def apply_closing(image, size):
    structure = np.ones((size, size), dtype=np.uint8)
    closed_image = binary_closing(image, structure=structure)
    return closed_image

# Function to identify and highlight closed points
def identify_closed_points(original, closed):
    return (closed > original).astype(np.uint8)

# Function to plot the original and closed images
def plot_closing_results(original, closed_images, closed_points, structure_sizes, output_path):
    fig, axes = plt.subplots(3, 3, figsize=(12, 12))
    
    # Show the original image in the first subplot
    axes[0, 0].imshow(original, cmap='gray_r')
    axes[0, 0].set_title("Original Image")
    axes[0, 0].axis('off')

    # Show the closed images and highlighted points in the other subplots
    for i, size in enumerate(structure_sizes):
        row, col = divmod(i + 1, 3)        
        # Display the closed image
        # Combine grayscale with a red overlay for closed points
        base_image = np.stack([closed_images[i]] * 3, axis=-1)  # Convert grayscale to RGB
        base_image = 1 - (base_image / base_image.max())  # Normalize and invert grayscale

        # Create a red overlay for closed points
        overlay = np.zeros_like(base_image)
        overlay[..., 0] = closed_points[i]  # Assign red to closed points

        # Combine the base image with the overlay
        colored_image = base_image.copy()
        colored_image[closed_points[i] == 1] = overlay[closed_points[i] == 1]

        axes[row, col].imshow(colored_image)
        
        axes[row, col].set_title(f"Closing Structure: {size}x{size}")
        axes[row, col].axis('off')

    plt.savefig(output_path, bbox_inches='tight')
    plt.close()

# Main script
def process_images(structure_sizes,image_paths, out_path):
    

    for image_path in image_paths:
        # Read the TIFF image
        with rasterio.open(image_path) as src:
            image = src.read(1)  # Read the first band

        # Binarize the image
        binarized_image = binarize_image(image)

        # Apply binary closing with different structure sizes
        closed_images = [apply_closing(binarized_image, size) for size in structure_sizes]

        # Identify closed points
        closed_points = [identify_closed_points(binarized_image, closed) for closed in closed_images]

        output_file = f"{out_path}/{image_path.split('/')[-1].split('.')[0]}_closing_2-9.png"

        # Plot the results
        plot_closing_results(binarized_image, closed_images, closed_points, structure_sizes, output_file)
# Example usage
if __name__ == "__main__":
    structure_sizes = [2,3,4,5,6,7,8,9]
    crop_path = '/data1/crops/ir108_2013-2014-2015-2016_200K-300K_CMA/1/'
    out_path = '/home/Daniele/fig/cma_analysis/closing_algorithm/'
    image_paths = sorted(glob(f"{crop_path}*.tif"))[:10]
    process_images(structure_sizes, image_paths, out_path)
