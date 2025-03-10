import os
import numpy as np
import pandas as pd
from glob import glob
from scipy.ndimage import binary_closing, label
import rasterio

# Define paths and file pattern
input_folder = "/data1/crops/ir108_2013-2014-2015-2016_200K-300K_CMA/1"
file_pattern = "*_EXPATS_0_200K-300K_greyscale_CMA.tif"
output_path = "/home/Daniele/fig/cma_analysis/modis/"

# Define structure for binary closing (3x3)
structure = np.ones((3, 3))

# List all matching files
file_list = sorted(glob(os.path.join(input_folder, file_pattern)))
print(len(file_list), "files found")

# # Initialize results list
# results = []

# for file in file_list:
#     print(f"Processing file: {file}")
    
#     # Open the TIFF file
#     with rasterio.open(file) as src:
#         image = src.read(1)  # Read the first band (greyscale)
    
#     # Binarize the image (values > 0 -> 1, otherwise -> 0)
#     binary_image = (image > 0).astype(int)
    
#     # Apply closing algorithm
#     closed_image = binary_closing(binary_image, structure=structure)
    
#     # Identify clear holes (0s surrounded by 1s)
#     holes = (closed_image == 1) & (binary_image == 0)
    
#     # Count the number of distinct holes
#     labeled_holes, num_holes = label(holes)
#     print(num_holes, "holes found")
    
#     # Store results
#     results.append({
#         "filename": os.path.basename(file),
#         "structure": "3x3",
#         "number_of_holes": num_holes
#     })


# # Convert results to a DataFrame
# results_df = pd.DataFrame(results)

# # Save the results to a CSV file
# output_csv = f"{output_path}holes_analysis_results.csv"
# results_df.to_csv(output_csv, index=False)
# print(f"Results saved to {output_csv}")

# Plot the histogram of the number of holes
import matplotlib.pyplot as plt

# Open the CSV file
results_df = pd.read_csv(f"{output_path}holes_analysis_results.csv")

tot_num_pixels = 128 * 128	
results_df['percentage_of_holes'] = results_df['number_of_holes'] / tot_num_pixels * 100

#get how many images have 0 holes
print("Images with 0 holes: ", results_df[results_df['number_of_holes'] == 0].shape[0])

fig, ax = plt.subplots(figsize=(7, 4))
ax.hist(results_df['percentage_of_holes'], bins=50, edgecolor='black')
plt.title("Distribution of the Number of Holes in Image Crops", fontsize=12, fontweight="bold")
plt.xlabel("Percentage of Holes")
plt.ylabel("Frequency")
plt.grid(True)
fig.savefig(f"{output_path}holes_distribution.png", dpi=300, bbox_inches="tight")
