import os
import h5py
from glob import glob
import xarray as xr
from osgeo import gdal

# Folder containing the HDF files
folder_path = '/data1/other_data/MODIS_cloud_properties/2013'

# List all files matching the pattern
#file_pattern = "MYD06_L2.A2013273.1320.061.2018049223922.hdf"
list_of_files = sorted(glob(f"{folder_path}/MYD06_L2*.hdf"))
print(list_of_files)
# Loop through files and open those matching the pattern
for file_path in list_of_files:

    # Open the HDF5 file
    dataset = gdal.Open(file_path)

    if dataset is None:
        print(f"Failed to open file: {file_path}")
    else:
        # Print metadata for the dataset
        print("Metadata:")
        metadata = dataset.GetMetadata()
        print(metadata)
        

        # Print available subdatasets
        subdatasets = dataset.GetSubDatasets()
        print("\nSubdatasets:")
        for subdataset in subdatasets:
            print(f"  {subdataset[0]} - {subdataset[1]}")

        # Open a subdataset (if available) for further exploration
        subdataset_path = subdatasets[0][0]  # Example: take the first subdataset
        subdataset = gdal.Open(subdataset_path)
        if subdataset is not None:
            print(f"Opened subdataset: {subdataset_path}")
            print(f"Subdataset shape: {subdataset.RasterXSize} x {subdataset.RasterYSize}")
        else:
            print("Failed to open subdataset")

            
        for subdataset in subdatasets:
            if 'Latitude' in subdataset[0]:
                lat_subdataset = subdataset[0]
            elif 'Longitude' in subdataset[0]:
                lon_subdataset = subdataset[0]
            elif 'Cloud_Top_Pressure' in subdataset[0]:
                cloud_top_pressure_subdataset = subdataset[0]

            # Open and read the data for Latitude, Longitude, and Cloud Top Pressure
            if lat_subdataset:
                lat_dataset = gdal.Open(lat_subdataset)
                lat_data = lat_dataset.ReadAsArray()
                print(lat_data)
            else:
                lat_data = None

            if lon_subdataset:
                lon_dataset = gdal.Open(lon_subdataset)
                lon_data = lon_dataset.ReadAsArray()
                print(lon_data)
            else:
                lon_data = None

            if cloud_top_pressure_subdataset:
                cloud_top_pressure_dataset = gdal.Open(cloud_top_pressure_subdataset)
                cloud_top_pressure_data = cloud_top_pressure_dataset.ReadAsArray()
                print(cloud_top_pressure_data)
            else:
                cloud_top_pressure_data = None
            exit()