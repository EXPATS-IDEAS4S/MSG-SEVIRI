import netCDF4 as nc

# Path to your NetCDF file
#path_to_files = '/home/daniele/Documenti/PhD_Cologne/Case_Studies/Germany_Flood_2021/CTH/'
#nc_file = 'CTXin20210712000000405SVMSGI1UD.nc'
path_to_files = "/net/ostro/figs_proposal_TEAMX/"
nc_file = "orography_expats_high_res.nc"

# Open the NetCDF file
dataset = nc.Dataset(path_to_files+nc_file, 'r')  # 'r' is for read mode

# Accessing global attributes
print("Global attributes:")
for attr in dataset.ncattrs():
    print(f"{attr}: {getattr(dataset, attr)}")

# Accessing dimensions
print("\nDimensions:")
for dim in dataset.dimensions.values():
    print(dim)

# Accessing variables
print("\nVariables:")
for var in dataset.variables:
    print(f"{var}: {dataset.variables[var]}")

"""
# Example of reading data from a variable
# Replace 'your_variable_name' with the actual variable name you want to access
variable_name = 'your_variable_name'
if variable_name in dataset.variables:
    variable_data = dataset.variables[variable_name][:]
    print(f"\nData for {variable_name}:")
    print(variable_data)
else:
    print(f"Variable {variable_name} not found in the file.")
"""

# Close the dataset
dataset.close()
