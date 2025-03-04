import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import binary_dilation, binary_erosion

output_folder = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/CMA/filling_cma_figs/'

# Create a small binary image with holes (10x10)
image = np.zeros((10, 10), dtype=int)
image[2:8, 3:7] = 1  # Add a solid rectangle
image[4, 4] = 0      # Create a hole
image[5, 5] = 0      # Create another hole
image[8, 3] = 1
image[1, 4] = 1
image[3, 2] = 1
image[5, 8] = 1

# Define a simple structuring element (3x3 square)
structuring_element = np.ones((3, 3), dtype=int)

# Define a simple structuring element (3x3 square)
structuring_element_size = (3, 3)

# Step 1: Apply Dilation
dilated_image = binary_dilation(image, structure=structuring_element)

# Step 2: Apply Erosion
closed_image = binary_erosion(dilated_image, structure=structuring_element)

# Visualize the steps
fig, axes = plt.subplots(1, 3, figsize=(7, 2))
titles = ['Original Image', 'Dilation', 'Dilation+Erosion (Closing)']

# Highlight the structuring element size in the original image
axes[0].imshow(image, cmap='gray', interpolation='nearest')
axes[0].set_title(titles[0])
axes[0].axis('off')

# Add a red rectangle to indicate the structuring element size
se_rect_top_left = (3, 4)  # Coordinates for the top-left corner of the SE
se_height, se_width = structuring_element_size
rect = plt.Rectangle((se_rect_top_left[1] - 0.5, se_rect_top_left[0] - 0.5), 
                     se_width, se_height, linewidth=1.5, edgecolor='red', facecolor='none')
axes[0].add_patch(rect)

# Dilated Image
axes[1].imshow(dilated_image, cmap='gray', interpolation='nearest')
axes[1].set_title(titles[1])
axes[1].axis('off')

# Closed Image
axes[2].imshow(closed_image, cmap='gray', interpolation='nearest')
axes[2].set_title(titles[2])
axes[2].axis('off')

plt.savefig(output_folder + 'closing_example.png', bbox_inches='tight')
