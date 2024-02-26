import eumdac
import os
import shutil
import time
import datetime
import requests
import logging
import concurrent.futures

# Start time
begin_time = time.time()

# Define the download directory
#download_dir = '/data/sat/msg/test/'  
download_dir = '/work/NWC_GEO/import/Sat_data/'  
os.makedirs(download_dir, exist_ok=True)

path_to_failed_file = download_dir+'failed_customizations.txt'
path_to_log_file = download_dir+'data_tailor_dani.log'

# Basic configuration of logging 
logging.basicConfig(level=logging.INFO, filename=path_to_log_file, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set your credentials (find them in EUMETSAT profile portal)
#import them from a py file: Daniele Credentials
from credentials import consumer_key, consumer_secret
credentials = (consumer_key, consumer_secret)

# Create an access token
token = eumdac.AccessToken(credentials)
logging.info(f"This token '{token}' expires {token.expiration}")

# Initialize DataStore and DataTailor
datastore = eumdac.DataStore(token)
datatailor = eumdac.DataTailor(token)

# Improved deletion of older customization jobs
for customisation in datatailor.customisations:
    if customisation.status not in ['DONE', 'FAILED']:
        logging.info(f'Delete completed customisation {customisation} from {customisation.creation_time} UTC.')
        try:
            customisation.delete()
            logging.info(f'Deleted {customisation.status} customisation {customisation} from {customisation.creation_time} UTC.')
        except eumdac.datatailor.CustomisationError as error:
            logging.error("Customisation Error: %s", error)
        except requests.exceptions.RequestException as error:
            logging.error("Request Error: %s", error)
    #in case you want to delete everything, add also this part
    if customisation.status in ['QUEUED', 'INACTIVE', 'RUNNING']:
        customisation.kill()
        logging.info(f'Delete {customisation.status} customisation {customisation} from {customisation.creation_time} UTC.')
        try:
            customisation.delete()
        except eumdac.datatailor.CustomisationError as error:
            logging.error("Customisation Error:", error)
        except Exception as error:
            logging.error("Unexpected error:", error)


# Specify the collection name
collection_name = 'EO:EUM:DAT:MSG:HRSEVIRI'
selected_collection = datastore.get_collection(collection_name)
logging.info(f"{selected_collection} - {selected_collection.title}")

# Define time span and geographical coordinates --> Ahr Floods July 2021
start = datetime.datetime(2021, 7, 12, 0, 0)
end = datetime.datetime(2021, 7, 16, 0, 0)
#north, south, east, west = 51.5, 42, 16, 5  #expats
north, south, east, west = 52, 48, 9, 5  #Germany Flood
format = 'hrit' #'msgnative','netcdf4',

# Search for data in the specified time span
data_items = selected_collection.search(dtstart=start, dtend=end)

# Check if the file already exists

# function to check if the file is already present in the downloading directory
def is_file_present(filename, download_dir, format):
    # Get the time string from the filenames after 'search' command 
    # example of name file before costumization: 
    # MSG4-SEVI-MSG15-0100-NA-20210714121243.449000000Z-NA 
    time_str = filename.split('.')[0].split('-')[-1]    

    # List all files in the download directory
    existing_files = os.listdir(download_dir)
    
    if format == 'hrit':
        # hrit filenames: H-000-MSG4__-MSG4________-WV_073___-000003___-202107141200-__
        # for each time there is a file for each channel and divided in 8 files
        #get the part of the datestring that refers to the minutes
        min_str = time_str[10:12]
        #switch the minutes that indicate the end of the scan to the minutes that indicate the 'rounded' start of the scan
        if '00'<min_str<'15': min_str='00'
        if '15'<min_str<'30': min_str='15' 
        if '30'<min_str<'45': min_str='30'
        if '45'<min_str<'59': min_str='45'
        time_str = time_str[0:10]+min_str 
        #count how many files have the correspoding timestring in the filename
        count = sum(1 for filename in existing_files if time_str in filename)
        #check if all the channels (11) and each single scan (8) + PRO and EPI are present
        if count == 90:
            return True
        return False
    else:   
        # Check if a file for this time period already exists
        for file in existing_files:
            # filename after costumization depends on the format:
            if format == 'msgnative':
                #nat filenames example: MSG3-SEVI-MSG15-0100-NA-20230731215741.559000000Z-NA.subset.nat
                time_str_cust = file.split('.')[0].split('-')
            elif format == 'netcdf4':
                #nc filename example: HRSEVIRI_20210715T101510Z_20210715T102742Z_epct_34b8524d_PC.nc
                time_str = time_str = time_str[:8] + 'T' + time_str[8:] + 'Z' # Insert 'T' after the 8th character and 'Z' at the end
                time_str_cust = file.split('.')[0].split('_')
            else:
                logging.warning("format not recognized.")
            #check if the timestring is in the filename
            if time_str in time_str_cust:    
                return True
        return False

# Filter data_items to exclude files that are already present 
data_items = [item for item in data_items if not is_file_present(str(item), download_dir, format)]

# Handle no data available
if not data_items:
    logging.warning("No data available for the specified time span.")
    exit()

logging.info(f'Found Datasets: {len(data_items)} datasets for the given time range')

#for item in data_items:
#    print(str(item))

# Define the customization chain for all channels and specified domain
chain = eumdac.tailor_models.Chain(
    product='HRSEVIRI',
    format= format, 
    #projection='geographic', #this is needed to get the lat/lon coordinates, but it slows down the process
    #roi={'NSWE': [north, south, west, east]} #roi dones't work with hrit format
)

# Process each data item
for item in data_items:
    try:
        # Send the customisation to Data Tailor Web Services
        customisation = datatailor.new_customisation(item, chain)
    except eumdac.datatailor.CustomisationError as error:
        logging.error("Customisation Error:", error)
        continue  # Skips to the next iteration of the for loop
    except requests.exceptions.RequestException as error:
        logging.error("Request Error:", error)
        continue  # Skips to the next iteration of the for loop

    # Flag to track if we should skip to the next item
    skip_to_next_item = False

    # Check the customisation status
    while customisation.status != 'DONE':
        logging.info(customisation.status)
        time.sleep(30)  # Pauses the script for 30 seconds between status checks

        if customisation.status == 'FAILED':
            # Write in a file the item that failed to be customized
            with open(path_to_failed_file, "a") as file:
                file.write(f"{item}\n")

            skip_to_next_item = True  # Set the flag to skip to the next item
            break  # Exit the while loop

    if skip_to_next_item:
        continue  # Skips to the next iteration of the for loop because of failure

   
    # # Use ThreadPoolExecutor to download files in parallel 
    # # (as customization isn't parallel using python maybe is not worthy to use this)
    # #function for downloading the data 
    # def download_file(customisation, output, download_dir):
    #     file_name = os.path.basename(output)
    #     file_path = os.path.join(download_dir, file_name)

    #     if not os.path.exists(file_path):
    #         try:
    #             with customisation.stream_output(output) as stream, open(file_path, mode='wb') as fdst:
    #                 shutil.copyfileobj(stream, fdst)
    #             return f"Downloaded {file_path}"
    #         except IOError as io_error:
    #             return f"IO Error while downloading {file_path}: {io_error}"
    #         except requests.exceptions.RequestException as request_error:
    #             return f"Request Error while downloading {file_path}: {request_error}"
    #     else:
    #         return f"File {file_path} already exists. Skipping download."
    # with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    #     # Create a future object for each file to be downloaded
    #     futures = [executor.submit(download_file, customisation, output, download_dir) 
    #                for output in customisation.outputs]

    #     # As each future completes, print its result
    #     for future in concurrent.futures.as_completed(futures):
    #         logging.info(future.result())

    #Dowload the customized data
    for output in customisation.outputs:
        file_name = os.path.basename(output)
        #file_name = output.split('/')[-1]
        file_path = os.path.join(download_dir, file_name)

        # Check if the file already exists 
        #TODO maybe this step is redundant if I check the existence of the file before the data tailor step
        if not os.path.exists(file_path):
            try:
                with customisation.stream_output(output) as stream, open(file_path, mode='wb') as fdst:
                    shutil.copyfileobj(stream, fdst)
                logging.info(f"Downloaded {file_path}")
            except requests.exceptions.HTTPError as http_error:
                # Specifically catching the HTTPError now
                logging.error(f"HTTP Error while downloading {file_path}: {http_error}")
                # For example, to specifically log unauthorized errors:
                if http_error.response.status_code == 401:
                    logging.error(f"Unauthorized access error for {file_path}. Check your authentication credentials.")
            except requests.exceptions.RequestException as request_error:
                logging.error(f"Request Error while downloading {file_path}: {request_error}")
            except IOError as io_error:
                logging.error(f"IO Error while downloading {file_path}: {io_error}")
        else:
            logging.info(f"File {file_path} already exists. Skipping download.")


    #The Data Tailor Web Service has a 20 Gb limit, so it's important to clear old customisations
    try:
        customisation.delete()
    except eumdac.datatailor.CustomisationError as error:
        logging.error("Customisation Deletion Error:", error)
    except requests.exceptions.RequestException as error:
        logging.error("Request Error during customisation deletion:", error)

logging.info("Data processing complete.")

#TODO try to customize and download the failed process
#if os.path.getsize(path_to_failed_file) > 0:
    
# End time
end_time = time.time()

# Calculate elapsed time
elapsed_time = end_time - begin_time
# Path to the text file where you want to save the elapsed time
output_file_path = download_dir+'elapsed_time_data_tailor.txt'

# Write elapsed time to the file
with open(output_file_path, 'w') as file:
    print(f"Elapsed time: {elapsed_time} seconds", file=file)