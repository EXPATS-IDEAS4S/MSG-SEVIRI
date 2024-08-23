import os
from PIL import Image

def create_gif_from_images(folder_path, output_gif_path, duration=500):
    """
    Creates a GIF from JPEG images stored in a specified folder.

    Parameters:
    - folder_path: str, the path to the folder containing the JPEG images.
    - output_gif_path: str, the path where the GIF should be saved.
    - duration: int, duration in milliseconds between frames in the GIF.
    """
    # Get a list of all JPEG images in the folder, sorted by filename
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.jpeg') and f.startswith('CMA')])

    # Create a list to store the images
    images = []

    for image_file in image_files:
        # Open each image and append to the list
        image_path = os.path.join(folder_path, image_file)
        img = Image.open(image_path)
        images.append(img)

    # Save the images as a GIF
    if images:
        images[0].save(
            output_gif_path,
            save_all=True,
            append_images=images[1:],
            duration=duration,
            loop=0
        )
        print(f"GIF saved to {output_gif_path}")
    else:
        print("No images found in the specified folder.")

# Example usage:
folder_path = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/full_domain_figs/IR_108_5th-95th'
output_gif_path = '/data/sat/msg/ml_train_crops/IR_108-WV_062-IR_039_2013-2014_128x128_EXPATS/full_domain_figs/CMA_IR_108_5th-95th.gif'

create_gif_from_images(folder_path, output_gif_path, duration=500)
