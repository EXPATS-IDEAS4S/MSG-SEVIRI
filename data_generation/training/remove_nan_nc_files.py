import os
import xarray as xr
import numpy as np

def remove_nc_files_with_nan(root_dir):
    """
    Recursively checks all .nc files in `root_dir` for NaN values
    and deletes the file if any NaNs are found.
    """
    removed_files = []

    for dirpath, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".nc"):
                filepath = os.path.join(dirpath, file)
                try:
                    ds = xr.open_dataset(filepath,engine="h5netcdf")
                    has_nan = False

                    for var in ds.data_vars:
                        if ds[var].isnull().any():
                            has_nan = True
                            break

                    ds.close()

                    if has_nan:
                        os.remove(filepath)
                        removed_files.append(filepath)
                        print(f"Removed file with NaNs: {filepath}")

                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
                    continue

    print(f"✅ Finished checking. {len(removed_files)} files removed.")
    return removed_files


remove_nc_files_with_nan("/data1/crops/dcv2_ir108_100x100_test_tensor/nc/1")
