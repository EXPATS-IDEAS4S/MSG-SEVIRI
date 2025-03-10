import os
import glob
from PIL import Image

def create_gif(input_folder, file_pattern, output_gif, duration=500):
    """
    Create a GIF from images matching a specific file pattern in a folder.
    
    Parameters:
        input_folder (str): The folder containing the images.
        file_pattern (str): The filename pattern (e.g., "*.png", "*.jpg").
        output_gif (str): The path to save the generated GIF.
        duration (int): Duration of each frame in milliseconds. Default is 500ms.
    """
    # Create the full path pattern
    file_path_pattern = os.path.join(input_folder, file_pattern)
    
    # Get a list of files matching the pattern
    image_files = sorted(glob.glob(file_path_pattern))
    if not image_files:
        print("No files found matching the pattern!")
        return
    
    # Load images
    images = [Image.open(img) for img in image_files]
    
    # Save images as GIF
    images[0].save(
        output_gif, 
        save_all=True, 
        append_images=images[1:], 
        duration=duration, 
        loop=0
    )
    print(f"GIF created and saved at {output_gif}")


year = 2014
# Folder containing images
input_folder = "/data/sat/msg/H_SAF/H10_fig/"
# File pattern to match
file_pattern = f'h10_{year}*_day_merged.png'	
# Output GIF file
output_gif = f"/data/sat/msg/H_SAF/H10_fig/output_{year}.gif"
# Frame duration in milliseconds
frame_duration = 300

create_gif(input_folder, file_pattern, output_gif, duration=frame_duration)
