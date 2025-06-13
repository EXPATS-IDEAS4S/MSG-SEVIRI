import pandas as pd
from datetime import datetime, timedelta
import os

def extract_lat_lon_grid(filename):
    parts = filename.split('_')
    lat, lon, grid = float(parts[1]), float(parts[2]), float(parts[3])
    return lat, lon, grid

def update_timestamp(filename, delta_hours):
    timestamp_str = filename.split('_')[0]  # e.g. '20160930-23:45'
    timestamp = datetime.strptime(timestamp_str, '%Y%m%d-%H:%M')
    new_timestamp = timestamp + timedelta(hours=delta_hours)
    return new_timestamp.strftime('%Y%m%d-%H:%M')

def build_new_filename(base_path, old_filename, new_timestamp):
    parts = old_filename.split('_')
    new_name = f"{new_timestamp}_{'_'.join(parts[1:])}"
    return os.path.join(base_path, new_name)

def process_csv(input_csv_path, output_csv_path, top_n=10):
    df = pd.read_csv(input_csv_path)
    print(df)

    exit()
    result_rows = []

    for label in df['label'].unique():
        label_df = df[df['label'] == label].nsmallest(top_n, 'distance')

        for _, row in label_df.iterrows():
            original_path = row['path']
            filename = os.path.basename(original_path)
            base_path = os.path.dirname(original_path)

            # Extract coordinates and grid size
            lat, lon, grid = extract_lat_lon_grid(filename)

            # Add original row
            result_rows.append(row.to_dict())

            # Add t - 12h
            new_ts_minus = update_timestamp(filename, -12)
            new_path_minus = build_new_filename(base_path, filename, new_ts_minus)
            row_minus = row.copy()
            row_minus['path'] = new_path_minus
            result_rows.append(row_minus.to_dict())

            # Add t + 12h
            new_ts_plus = update_timestamp(filename, 12)
            new_path_plus = build_new_filename(base_path, filename, new_ts_plus)
            row_plus = row.copy()
            row_plus['path'] = new_path_plus
            result_rows.append(row_plus.to_dict())

    # Create new DataFrame and save
    new_df = pd.DataFrame(result_rows)
    new_df.to_csv(output_csv_path, index=False)
    print(f"New CSV saved to {output_csv_path}")


general_path = "/data1/fig/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/closest/"
input_csv_path = f"{general_path}crop_list_dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA_100_closest.csv"  # Replace with your input CSV file path
output_csv_path = f"/data1/fig/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/test/centroids_evolution/crops_selection.csv"  # Replace with your desired output CSV file path

process_csv(input_csv_path, output_csv_path, top_n=10)
