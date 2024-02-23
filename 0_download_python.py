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
download_dir = '/work/MSG/'  
os.makedirs(download_dir, exist_ok=True)

path_to_failed_file = '/work/MSG/failed_customizations.txt'

# Basic configuration of logging 
logging.basicConfig(level=logging.INFO, filename=download_dir+'data_tailor_2.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Set your credentials (find them in EUMETSAT profile portal)
#Daniele Credentials
consumer_key = 'MwVGCDXIMtsN7Cj28dGBz4UcZYga'
consumer_secret = 'Lepxj10Ag3p2R5FVdpwvP08Ny_Ia'
#Claudia Credentials
#consumer_key = 'xoRBoRjjpsbmX2ZzBVY1UbKcmVAa'
#consumer_secret = 'owcUIfV6kGNupOl75P6xQ9vKrssa'

# For security resaon, they can be set up as enviromental variables using exports from the terminal, e.g.
# export CONSUMER_KEY=MwVGCDXIMtsN7Cj28dGBz4UcZYga
# export SECRET=Lepxj10Ag3p2R5FVdpwvP08Ny_Ia

#consumer_key = os.environ.get('CONSUMER_KEY')
#consumer_secret = os.environ.get('SECRET')

# Handle cases where environment variables are not set
#if not consumer_key or not consumer_secret:
#    raise EnvironmentError("Consumer key or secret not found in environment variables")
#    #logging.warning("Consumer key or secret not found in environment variables")
#    exit()

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
start = datetime.datetime(2023, 7, 16, 0, 0)
end = datetime.datetime(2023, 8, 1, 0, 0)
north, south, east, west = 51.5, 42, 16, 5  #expats
#north, south, east, west = 52, 48, 9, 5  #Germany Flood

# Search for data in the specified time span
data_items = selected_collection.search(dtstart=start, dtend=end)

# Check if the file already exists

# function to check if the file is already present in the downloading directory
def is_file_present(filename, download_dir):
    #Assuming the the file format are the following:
    #example of name file before costumization: 
    #MSG4-SEVI-MSG15-0100-NA-20210714121243.449000000Z-NA
    #exaple of name file after costumization (in the download directory):
    #if nat file are downloded 
    #MSG3-SEVI-MSG15-0100-NA-20230731215741.559000000Z-NA.subset.nat
    #if nc files are downloaded
    #HRSEVIRI_20210715T101510Z_20210715T102742Z_epct_34b8524d_PC.nc
    time_str = filename.split('-')[5].split('.')[0]
    #start_time = datetime.strptime(start_time_str, "%Y%m%dT%H%M%SZ")

    # Insert 'T' after the 8th character and 'Z' at the end
    #time_str = time_str[:8] + 'T' + time_str[8:] + 'Z'

    # List all files in the download directory
    existing_files = os.listdir(download_dir)
    
    # Check if a file for this time period already exists
    for file in existing_files:
        #if file.startswith("HRSEVIRI_") and time_str in file.split('_'):
        if time_str in file.split('.')[0].split('-'):    
            return True
    return False

# Filter data_items to exclude files that are already present TODO not possible because item names are different from the downloaded custmized products
data_items = [item for item in data_items if not is_file_present(str(item), download_dir)]

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
    format='msgnative', #'netcdf4',
    #projection='geographic', #this is needed to get the lat/lon coordinates, but it slows down the process
    roi={'NSWE': [north, south, west, east]}
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

            # # Optionally, delete the failed customisation
            # try:
            #     customisation.delete()
            # except (eumdac.datatailor.CustomisationError, requests.exceptions.RequestException) as error:
            #     logging.error("Error during customisation deletion:", error)

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
            except IOError as io_error:
                logging.error(f"IO Error while downloading {file_path}: {io_error}")
            except requests.exceptions.RequestException as request_error:
                logging.error(f"Request Error while downloading {file_path}: {request_error}")
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