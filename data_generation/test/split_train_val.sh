#!/bin/bash
# This script randomly splits a dataset into train/val/test.
# Each class should be a subfolder in INPUT_DIR.

set -e

# 🔧 SETTINGS (edit here)
INPUT_DIR="/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm/nc"   # dataset with class subfolders
OUTPUT_DIR="/sat_data/crops/2006-2023_4-9_areathresh30_res15min_5frames_gap15min_cropsize75_min5pix_IR108-cm"    # where to save splits
TRAIN_RATIO=75     # percentage for training
VAL_RATIO=15       # percentage for validation
TEST_RATIO=10      # percentage for testing
COPY_OR_MOVE="cp"  # set to "mv" to move instead of copy

# -----------------------------

# check ratios
if (( TRAIN_RATIO + VAL_RATIO + TEST_RATIO != 100 )); then
  echo "❌ Ratios must add up to 100 (train=$TRAIN_RATIO, val=$VAL_RATIO, test=$TEST_RATIO)"
  exit 1
fi

mkdir -p "$OUTPUT_DIR/train" "$OUTPUT_DIR/val" "$OUTPUT_DIR/test"

for class_dir in "$INPUT_DIR"/*; do
  if [ -d "$class_dir" ]; then
    class_name=$(basename "$class_dir")
    echo "Processing class: $class_name"

    mkdir -p "$OUTPUT_DIR/train/$class_name"
    mkdir -p "$OUTPUT_DIR/val/$class_name"
    mkdir -p "$OUTPUT_DIR/test/$class_name"

    # List files and shuffle
    mapfile -t files < <(find "$class_dir" -type f | shuf)
    total=${#files[@]}
    train_count=$(( total * TRAIN_RATIO / 100 ))
    val_count=$(( total * VAL_RATIO / 100 ))
    test_count=$(( total - train_count - val_count ))  # remainder goes to test

    # Copy/move train split
    for ((i=0; i<train_count; i++)); do
      $COPY_OR_MOVE "${files[$i]}" "$OUTPUT_DIR/train/$class_name/"
    done

    # Copy/move val split
    for ((i=train_count; i<train_count+val_count; i++)); do
      $COPY_OR_MOVE "${files[$i]}" "$OUTPUT_DIR/val/$class_name/"
    done

    # Copy/move test split
    for ((i=train_count+val_count; i<total; i++)); do
      $COPY_OR_MOVE "${files[$i]}" "$OUTPUT_DIR/test/$class_name/"
    done

    echo " → $train_count train / $val_count val / $test_count test"
  fi
done

echo "✅ Done! Splits saved in $OUTPUT_DIR"
