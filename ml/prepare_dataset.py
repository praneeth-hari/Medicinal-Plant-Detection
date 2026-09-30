import os
import shutil
import random
import sys
from pathlib import Path

# All paths relative to project root (parent of ml/)
_ROOT_DIR = Path(__file__).resolve().parent.parent

# Target directories
SOURCE_DIR = str(_ROOT_DIR / "data" / "raw")
DEST_DIR = str(_ROOT_DIR / "data")

TRAIN_PCT = 0.70
VAL_PCT = 0.15
TEST_PCT = 0.15

def split_dataset():
    if not os.path.exists(SOURCE_DIR):
        print(f"Error: Source directory {SOURCE_DIR} does not exist.")
        sys.exit(1)

    classes = [d for d in os.listdir(SOURCE_DIR) if os.path.isdir(os.path.join(SOURCE_DIR, d))]
    print(f"Found {len(classes)} class folders in source dataset.")
    
    # 1. Verification of class sizes
    class_sizes = {}
    for c in classes:
        class_path = os.path.join(SOURCE_DIR, c)
        files = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]
        class_sizes[c] = len(files)
        
        # Abort check
        if len(files) < 30:
            print(f"Abort Error: Class '{c}' has only {len(files)} images (fewer than 30 required).")
            sys.exit(1)

    print("\n--- Class Image Counts & Imbalance Check ---")
    total_images = sum(class_sizes.values())
    avg_images = total_images / len(classes)
    
    for c, size in sorted(class_sizes.items()):
        imbalance_pct = ((size - avg_images) / avg_images) * 100
        print(f"Class: {c:<15} | Count: {size:<4} | Diff from Avg: {imbalance_pct:>+6.1f}%")

    # Clear destination subfolders
    for split in ["train", "val", "test"]:
        split_path = os.path.join(DEST_DIR, split)
        if os.path.exists(split_path):
            shutil.rmtree(split_path)
        os.makedirs(split_path, exist_ok=True)

    # 2. Split and Copy
    random.seed(42)  # For reproducibility
    print("\nSplitting images...")
    
    split_stats = {
        "train": 0,
        "val": 0,
        "test": 0
    }

    for c in classes:
        class_path = os.path.join(SOURCE_DIR, c)
        files = [f for f in os.listdir(class_path) if os.path.isfile(os.path.join(class_path, f))]
        
        # Filter only supported image files (exclude .gif/.webp which cause training issues)
        image_files = [f for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        random.shuffle(image_files)
        
        n_total = len(image_files)
        n_train = int(n_total * TRAIN_PCT)
        n_val = int(n_total * VAL_PCT)
        # Give remaining to test
        
        train_files = image_files[:n_train]
        val_files = image_files[n_train:n_train + n_val]
        test_files = image_files[n_train + n_val:]
        
        # Create directories
        for split in ["train", "val", "test"]:
            os.makedirs(os.path.join(DEST_DIR, split, c), exist_ok=True)
            
        # Copy files
        for f in train_files:
            shutil.copy(os.path.join(class_path, f), os.path.join(DEST_DIR, "train", c, f))
            split_stats["train"] += 1
        for f in val_files:
            shutil.copy(os.path.join(class_path, f), os.path.join(DEST_DIR, "val", c, f))
            split_stats["val"] += 1
        for f in test_files:
            shutil.copy(os.path.join(class_path, f), os.path.join(DEST_DIR, "test", c, f))
            split_stats["test"] += 1

    print("\n--- Splitting Statistics ---")
    print(f"Total Images Copied: {sum(split_stats.values())}")
    print(f"  - Train:      {split_stats['train']} ({split_stats['train']/sum(split_stats.values())*100:.1f}%)")
    print(f"  - Validation: {split_stats['val']} ({split_stats['val']/sum(split_stats.values())*100:.1f}%)")
    print(f"  - Test:       {split_stats['test']} ({split_stats['test']/sum(split_stats.values())*100:.1f}%)")

if __name__ == "__main__":
    split_dataset()
