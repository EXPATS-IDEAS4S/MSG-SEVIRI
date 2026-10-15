import pandas as pd
from datetime import datetime, timedelta
import os

def parse_filename(filename):
    """
    Extract date, time, lat, lon, grid size from filename.
    """
    basename = os.path.basename(filename)
    parts = basename.split('_')
    date_time = parts[0]            # e.g. '20140528-02:00'
    lat = float(parts[1])
    lon = float(parts[2])
    grid_size = float(parts[3])

    date_str, time_str = date_time.split('-')
    return date_str, time_str, lat, lon, grid_size

def generate_time_offsets(date_str, time_str, delta_minutes=15, steps=12):
    """
    Generate timestamps from t-12*delta to t+12*delta (inclusive).
    Returns list of (date, time) tuples.
    """
    base_dt = datetime.strptime(f"{date_str} {time_str}", "%Y%m%d %H:%M")
    return [
        (dt.strftime("%Y%m%d"), dt.strftime("%H:%M"))
        for dt in (base_dt + timedelta(minutes=delta_minutes * i) for i in range(-steps, steps + 1))
    ]

def process_csv(input_path, output_path, top_n=10, delta_minutes=15, steps=48):
    df = pd.read_csv(input_path)
    result_rows = []

    #remove invalid rows labels -100
    df = df[df['label'] != -100]

    for label in df['label'].unique():
        top_rows = df[df['label'] == label].nlargest(top_n, 'distance')

        for _, row in top_rows.iterrows():
            path = row['path']
            date_str, time_str, lat, lon, grid_size = parse_filename(path)
            print(f"Processing: {path} | Date: {date_str} | Time: {time_str} | Lat: {lat} | Lon: {lon} | Grid Size: {grid_size}")

            time_offsets = generate_time_offsets(date_str, time_str, delta_minutes, steps)
            print(f"Generated {len(time_offsets)} time offsets for {date_str} {time_str}")
            print(time_offsets )
         
            for new_date, new_time in time_offsets:
                result_rows.append({
                    'date': new_date,
                    'time': new_time,
                    'ul_lat': lat,
                    'ul_lon': lon,
                    'grid_size': grid_size,
                    'label': row['label'],
                    'distance': row['distance']
                })

    result_df = pd.DataFrame(result_rows)
    result_df.to_csv(output_path, index=False)
    print(f"Saved expanded CSV to: {output_path}")



general_path = "/data1/fig/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/closest/"
input_csv_path = f"{general_path}crop_list_dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA_1000_closest.csv"  # Replace with your input CSV file path
output_csv_path = f"/data1/fig/dcv2_ir108_128x128_k9_expats_70k_200-300K_CMA/test/centroids_evolution/crops_selection.csv"  # Replace with your desired output CSV file path

process_csv(input_csv_path, output_csv_path, top_n=10)
