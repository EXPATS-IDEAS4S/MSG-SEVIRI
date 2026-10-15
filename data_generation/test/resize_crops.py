import os
import glob
import xarray as xr
import numpy as np
import random
import shutil

def preprocess_netcdf_dataset(root_folder, target_size=(75, 75)):
    target_h, target_w = target_size
    processed, deleted = 0, 0

    for nc_file in glob.glob(os.path.join(root_folder, "*/*.nc")):
        try:
            ds = xr.open_dataset(nc_file, engine="h5netcdf")

            # get spatial dims
            H = ds.dims.get("lat", None)
            W = ds.dims.get("lon", None)

            if H is None or W is None:
                print(f"Skipping {nc_file}: no lat/lon dims")
                ds.close()
                continue

            if H < target_h or W < target_w:
                print(f"Deleting {nc_file}: smaller than target ({H}, {W})")
                ds.close()
                os.remove(nc_file)
                deleted += 1
                continue

            if H > target_h or W > target_w:
                # random crop indices
                top = random.randint(0, H - target_h)
                left = random.randint(0, W - target_w)

                ds = ds.isel(lat=slice(top, top + target_h),
                             lon=slice(left, left + target_w))

            # save back
            tmp_file = nc_file + ".tmp"
            ds.to_netcdf(tmp_file, engine="h5netcdf")
            ds.close()
            shutil.move(tmp_file, nc_file)
            processed += 1

        except Exception as e:
            print(f"Error processing {nc_file}: {e}")

    print(f"✅ Done! Processed: {processed}, Deleted: {deleted}")


# Example usage:
preprocess_netcdf_dataset("/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/test", 
                          target_size=(75, 75))
