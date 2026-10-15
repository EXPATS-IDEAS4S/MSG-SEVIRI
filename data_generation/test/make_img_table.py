import os
import re
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
from glob import glob
import imageio

# === CONFIGURATION ===
IMG_DIR = "/data1/crops/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/test/centroids_evolution/img/1"
OUTPUT_DIR = "/data1/crops/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/test/centroids_evolution/gif_frames"
GIF_PATH = "/data1/crops/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/test/centroids_evolution/evolution.gif"
N_COLS = 10
CMAP = 'gray'
GIF_DURATION = 1000  # milliseconds per frame
CREATE_TABLES = False  # Set to True if you want to create tables for each timestep
# ======================

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --- Helper to parse each filename ---
def parse_filename(fname):
    """
    #Extracts label, distance, sample_idx, timestep, and timestamp from filename.
    """
    pattern = r"label-(\d+)_dist-([\d\.]+)_ul-[\d\.]+_[\d\.]+_(\d+)_\d+_(t\d+)_(\d{4}-\d{2}-\d{2}T\d{2}-\d{2})"
    match = re.search(pattern, fname)
    if match:
        label = int(match.group(1))
        dist = float(match.group(2))
        sample_idx = int(match.group(3))
        timestep = match.group(4)
        timestamp = match.group(5)
        return label, dist, sample_idx, timestep, timestamp
    return None

# --- Load all parsed image info into a DataFrame ---
records = []
for path in glob(os.path.join(IMG_DIR, "*.png")):
    fname = os.path.basename(path)
    parsed = parse_filename(fname)
    if parsed:
        label, dist, sample_idx, timestep, timestamp = parsed
        records.append({
            "path": path,
            "label": label,
            "distance": dist,
            "sample_idx": sample_idx,
            "timestep": timestep,
            "timestamp": timestamp
        })

df = pd.DataFrame(records)
time_steps = sorted(df['timestep'].unique(), key=lambda x: int(x[1:]))

# --- Step 1: Get sample_idx ordering from t0 for each label ---
t0_df = df[df['timestep'] == 't0']
fixed_sample_order = {}

for label in sorted(t0_df['label'].unique()):
    label_df = t0_df[t0_df['label'] == label].sort_values(by='distance', ascending=False)
    fixed_sample_order[label] = label_df['sample_idx'].head(N_COLS).tolist()

# --- Step 2: Plot a table for a single timestep ---
def plot_fixed_table(df_step, timestep, timestamp, output_dir, fixed_order_dict, n=N_COLS):
    labels = sorted(fixed_order_dict.keys())
    num_labels = len(labels)
    fig, axes = plt.subplots(num_labels, n, figsize=(n * 2, num_labels * 2))
    #fig.suptitle(f"Timestep {timestep}", fontsize=16, fontweight="bold")

    if num_labels == 1:
        axes = np.expand_dims(axes, axis=0)

    for i, label in enumerate(labels):
        label_df = df_step[df_step['label'] == label]
        sample_indices = fixed_order_dict[label]

        for j, sample_idx in enumerate(sample_indices):
            sample_row = label_df[label_df['sample_idx'] == sample_idx]
            ax = axes[i, j] if num_labels > 1 else axes[j]

            if not sample_row.empty:
                img_path = sample_row.iloc[0]['path']
                img = Image.open(img_path).convert('L')
                ax.imshow(img, cmap=CMAP)
            else:
                ax.imshow(np.ones((128, 128)) * 255, cmap=CMAP)  # white placeholder

            ax.axis('off')
            if j == 0:
                ax.set_ylabel(f"Label {label}", fontsize=12, fontweight='bold', rotation=0, labelpad=30, va='center')

    # Column headers = sample indices
    #for j in range(n):
    #    axes[0, j].set_title(f"{sample_indices[j]}", fontsize=10)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    #save with 2 digits for timestep
    out_path = os.path.join(output_dir, f"table_{timestep:02d}.png")
    plt.savefig(out_path, bbox_inches='tight', dpi=200)
    plt.close()
    print(f"Saved frame: {out_path}")
    return out_path


if CREATE_TABLES:
    # --- Step 3: Generate all frames ---
    frame_paths = []
    for t in time_steps:
        df_step = df[df['timestep'] == t]
        ts_timestamp = df_step['timestamp'].iloc[0] if not df_step.empty else "unknown"
        frame_path = plot_fixed_table(df_step, t, ts_timestamp, OUTPUT_DIR, fixed_sample_order)
        frame_paths.append(frame_path)
else:
    #get already existing frames
    frame_paths = sorted(glob(os.path.join(OUTPUT_DIR, "*.png")))
    print(frame_paths)


# --- Step 4: Create GIF ---
images = [imageio.v2.imread(p) for p in frame_paths]
imageio.mimsave(GIF_PATH, images, duration=GIF_DURATION)
print(f"\n✅ GIF saved to: {GIF_PATH}")
