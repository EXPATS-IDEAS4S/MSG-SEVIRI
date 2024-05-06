# check_file_presence.py
import os
import sys
import logging
import glob

def timestamp_from_file(file, format):
    # filename after costumization depends on the format:
    if format == 'msgnative':
        #nat filenames example: MSG3-SEVI-MSG15-0100-NA-20230731215741.559000000Z-NA.subset.nat
        file_timestamp = file.split('.')[0].split('-')[5]

    elif format == 'netcdf4':
        #nc filename example: HRSEVIRI_20210715T101510Z_20210715T102742Z_epct_34b8524d_PC.nc
        file_timestamp = file.split('.')[0].split('_')[2].replace('T', '')
    
    return file_timestamp

def get_existing_timestamps(download_dir, format):
    # create empty list of existing files
    existing_files = []

    # List all files with given format in the download directory and subdirectories
    if format == 'hrit' or format == 'hrit_compressed':
        existing_files = glob.glob(f'{download_dir}/**/*.hrit', recursive=True)
    
    elif format == 'msgnative':
        existing_files = glob.glob(f'{download_dir}/**/*.nat', recursive=True)
        
    elif format == 'netcdf4':
        existing_files = glob.glob(f'{download_dir}/**/*.nc', recursive=True)
    
    # loop over files and only keep the timestamps
    existing_files = [timestamp_from_file(f, format) for f in existing_files]
    return existing_files


def timestamp_from_product(product_name):
    # Get the time string from the filenames after 'search' command 
    # example of name file before costumization: 
    # MSG4-SEVI-MSG15-0100-NA-20210714121243.449000000Z-NA 
    product_timestamp = product_name.split('.')[0].split('-')[-1]
    return product_timestamp

def delete_existing_products(product_file, download_dir, format):

    # if download_dir does not even exists - no files will exists so return without deleting any products
    if not os.path.exists(download_dir):
        return
    
    # read all timestamps of existing files
    existing_timestamps = get_existing_timestamps(download_dir, format)
    print('existing timestamps', len(existing_timestamps), existing_timestamps[:2])

    # read all products that are planned to be downloaded
    with open(product_file, "r") as f:
        products = f.readlines()

    print("products before deleting", len(products))

    products_to_download = [p for p in products if timestamp_from_product(p) not in existing_timestamps]

    # write those that still need to be downloaded to same file
    with open(product_file, "w") as prod_file:
        for prod in products:
            # if timestamp is not existing
            if timestamp_from_product(prod) not in existing_timestamps:
                # write to file
                prod_file.write(prod)
                
    print('products', len(products_to_download), products_to_download)


if __name__ == "__main__":
    # Arguments passed from bash script
    product_file = sys.argv[1].strip()
    download_dir = sys.argv[2]
    format = sys.argv[3]

    delete_existing_products(product_file, download_dir, format)
    print("successfully deleted existing products.")