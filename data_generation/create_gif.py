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
    image_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.png') ])

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
folder_path = '/data1/crops/npy_crops_test/png'
output_gif_path = '/data1/crops/npy_crops_test/png/IR_108_07-07-2014_expats.gif'

create_gif_from_images(folder_path, output_gif_path, duration=500)
