import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from glob import glob
import xarray as xr

# Paths
modis_cma_path = '/data1/other_data/MODIS/2013/'
modis_filename = 'CLDMSK_L2_MODIS_Aqua*.nc'
output_path = '/home/Daniele/fig/cma_analysis/modis/'

# File pattern and list
filepattern = modis_cma_path + modis_filename
filelist = sorted(glob(filepattern))
print(f"Found {len(filelist)} files")

# Placeholder for parsed timestamps
timestamps = []

# Extract timestamps
for file_path in filelist:
    ds = xr.open_dataset(file_path)
    time_start = ds.attrs.get("time_coverage_start", None)  # Extract time coverage start

    if time_start:
        timestamps.append(pd.to_datetime(time_start))  # Convert to datetime object

# Ensure timestamps are parsed correctly
if not timestamps:
    print("No valid timestamps found. Check the files and their attributes.")
    exit()

# Step 1: Aggregate by day
timestamps_series = pd.Series(timestamps)  # Convert to Pandas Series for manipulation
overpasses_per_day = timestamps_series.dt.floor('D').value_counts().sort_index()  # Group by day

# Step 2: Create a DataFrame for plotting
overpasses_df = overpasses_per_day.reset_index()
overpasses_df.columns = ['Date', 'Overpasses']
print(overpasses_df)

# Step 3: Plot
plt.figure(figsize=(14, 6))
plt.bar(overpasses_df['Date'], overpasses_df['Overpasses'], width=0.8, color='skyblue', edgecolor='black')
plt.title("Number of Overpasses per Day", fontsize=16, fontweight="bold")
plt.xlabel("Date", fontsize=12)
plt.ylabel("Overpass Count", fontsize=12)
plt.xticks(
    ticks=overpasses_df['Date'][::15],  # Adjust tick frequency for readability
    labels=overpasses_df['Date'][::15].dt.strftime("%Y-%m-%d"),
    rotation=45,
    fontsize=10,
    ha='right'
)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig(f"{output_path}modis_overpasses_per_day.png")

