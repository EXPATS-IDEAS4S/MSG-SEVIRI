import os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import binary_closing
import matplotlib as mpl

# === CONFIGURATION ===
MAIN_DIR = "/data1/crops/ir108_100x100_2013-2020_3xrandomcrops_1xtimestamp_cma_nc"
INPUT_DIR = f"{MAIN_DIR}/nc/1/"
VAR_NAME = ["IR_108", 'SYNMSG_BT_CL_IR10.8']  # Can be single (e.g., "IR_108") or combined (e.g., "WV_062-IR_108")
OUTPUT_DIR = f"{MAIN_DIR}/img/IR_108/"

# ======================
def create_WV_IR_diff_colormap(vmin, center, vmax, diverg_cmap=mpl.cm.seismic):
    if vmin is None:
        vmin = -1
    if vmax is None:
        vmax = 1
    # get number of colors above and below center point representing the respective range percentages
    n_pos = int(265*(vmax-center)/(vmax-vmin)) if vmax > center else 1
    n_neg = int(265*(center-vmin)/(vmax-vmin)) if vmin < center else 1
    # sample colors
    colors_pos = diverg_cmap(np.linspace(0.7, 1, n_pos))
    colors_neg = diverg_cmap(np.linspace(0, 0.5, n_neg))
    # combine them and build a new colormap
    colors = np.vstack((colors_neg, colors_pos))
    
    return mpl.colors.LinearSegmentedColormap.from_list('recentered_cmap', colors)


def normalize_data(data, vmin=None, vmax=None):
    if vmin is None:
        vmin = np.nanmin(data)
    if vmax is None:
        vmax = np.nanmax(data)
    return np.clip((data - vmin) / (vmax - vmin), 0, 1)

def save_image(data, out_path, cmap='viridis', vmin=None, vmax=None):
    plt.imsave(out_path, data, cmap=cmap, vmax=vmax, vmin=vmin)
    print(f"Saved: {out_path}")

def is_combined_channel(var_name):
    return "-" in var_name

def combine_channels(ds, var_names, time_index, method='subtract'):
    """Load and combine channels from a dataset using the given method."""
    if not all(var in ds for var in var_names):
        raise ValueError(f"One or more variables not found: {var_names}")

    data = []
    for var in var_names:
        img = ds[var].sel(time=ds.time[time_index]).squeeze().values
        data.append(img)

    if method == 'subtract':
        return data[0] - data[1]
    elif method == 'average':
        return np.mean(data, axis=0)
    else:
        raise ValueError(f"Unknown combine method: {method}")

def convert_nc_to_images(input_dir, output_dir, var_name="IR_108", cmap="plasma", vmin=None, vmax=None):
    os.makedirs(output_dir, exist_ok=True)
    nc_files = sorted([f for f in os.listdir(input_dir) if f.endswith(".nc")])
    print(f"Found {len(nc_files)} .nc files in {input_dir}.")

    # Accept either a single name or a list of candidate names.
    candidates = var_name if isinstance(var_name, list) else [var_name]

    for nc_file in nc_files:
        print(f"Processing {nc_file}...")
        nc_path = os.path.join(input_dir, nc_file)
        try:
            with xr.open_dataset(nc_path, engine='h5netcdf') as ds:
                print(ds.time.values)

                # Use the first candidate variable that exists in this file.
                resolved_var = next((v for v in candidates if v in ds), None)
                if resolved_var is None:
                    print(f"None of {candidates} found in {nc_file}. Skipping.")
                    continue
                print(f"Using variable: {resolved_var}")

                for i, t in enumerate(ds.time.values):
                    print(f"Processing time step {i} for time {t}...")

                    img = ds[resolved_var].sel(time=t).squeeze().values

                    # Apply cloud mask if available
                    if 'cma' in ds and 'IR_108' in resolved_var:
                        cma = ds['cma'].sel(time=t).squeeze().values
                        cma = binary_closing(cma, structure=np.ones((3, 3), dtype=bool))
                        fill_value = vmax if vmax is not None else float(np.nanmax(img))
                        img[cma == 0] = fill_value

                    timestamp = str(np.datetime_as_string(t, unit='m')).replace(':', '-')
                    out_name = f"{os.path.splitext(nc_file)[0]}_t{i}_{timestamp}.png"
                    out_path = os.path.join(output_dir, out_name)
                    save_image(img, out_path, cmap=cmap, vmin=vmin, vmax=vmax)

        except Exception as e:
            print(f"Error processing {nc_file}: {e}")

if __name__ == "__main__":
    cmap = "gray_r"
    vmin = 240 #200
    vmax = 320 #260
    #vmin, center, vmax = -60, 0, 5
    #cmap = create_WV_IR_diff_colormap(vmin, center, vmax)
    convert_nc_to_images(
        input_dir=INPUT_DIR,
        output_dir=OUTPUT_DIR,
        var_name=VAR_NAME,
        cmap=cmap,
        vmin=vmin,
        vmax=vmax
    )

#2176342