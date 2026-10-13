"""
predict.py — Inference Script
============================================================
Handles single-image classification, loading plant_classifier.pth, 
preprocessing, and matching class indexes to mapped common plant names.
"""
from __future__ import annotations

import os
import sys
import json
import threading
import torch
from pathlib import Path
from PIL import Image
from torchvision import transforms

# Set path relative to project root
_ML_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _ML_DIR.parent
sys.path.insert(0, str(_ROOT_DIR))

from ml.model import PlantClassifier

# Configured paths (portable, relative to project root)
MODEL_PATH = str(_ROOT_DIR / "backend" / "data" / "models" / "plant_classifier.pth")
MAPPING_PATH = str(_ROOT_DIR / "backend" / "data" / "models" / "class_mapping.json")

# ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Alias dictionary to map folder labels to database seeded common names
_ALIAS_MAP = {
    "aloevera": "Aloe Vera",
    "amruthaballi": "Giloy",
    "bhrami": "Brahmi",
    "bringaraja": "Bhringraj",
    "amla": "Amla",  # Direct match mapping
    "curry": "Curry Leaves",
    "drumstick": "Moringa",
}

# Thread-safe lazy-loaded model singleton
_model = None
_class_names: list[str] = []
_device: torch.device | None = None
_load_lock = threading.Lock()

def load_inference_model() -> tuple["PlantClassifier", list[str]]:
    """Load model weights and class mappings if not already loaded (thread-safe)."""
    global _model, _class_names, _device
    if _model is not None:
        return _model, _class_names

    with _load_lock:
        # Double-check after acquiring lock
        if _model is not None:
            return _model, _class_names

        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model checkpoint not found at: {MODEL_PATH}")
        if not os.path.exists(MAPPING_PATH):
            raise FileNotFoundError(f"Class mapping index not found at: {MAPPING_PATH}")

        with open(MAPPING_PATH, "r", encoding="utf-8") as f:
            _class_names = json.load(f)

        _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # Initialize model with correct number of output classes
        _model = PlantClassifier.load_checkpoint(MODEL_PATH, num_classes=len(_class_names))
        _model = _model.to(_device)

    return _model, _class_names

def map_class_name(name: str) -> str:
    """Map class folder names to dynamic database common names."""
    clean_name = name.strip()
    lower_name = clean_name.lower()
    
    # Check alias dictionary
    if lower_name in _ALIAS_MAP:
        return _ALIAS_MAP[lower_name]
        
    # Default: replace underscores with spaces and title-case
    return clean_name.replace("_", " ").title()

def generate_inference_crops(img: Image.Image, size: int = 224) -> list[Image.Image]:
    """Generate multi-scale crops to capture both macro leaf arrangement and micro leaf venation."""
    from PIL import ImageOps
    w, h = img.size
    crops = [
        img.resize((size, size), Image.Resampling.BILINEAR),
        ImageOps.fit(img, (size, size), centering=(0.5, 0.5)),
    ]
    # For non-square or high-res images, add regional leaf cluster zooms
    if max(w, h) >= 300:
        crops.append(ImageOps.fit(img, (size, size), centering=(0.25, 0.5)))
        crops.append(ImageOps.fit(img, (size, size), centering=(0.75, 0.5)))
        crops.append(ImageOps.fit(img, (size, size), centering=(0.5, 0.25)))
    return crops


def predict(image_path: str, top_k: int = 5) -> dict:
    """Run inference on a single image using multi-crop ensembling.

    Args:
        image_path: Path to the input image file.
        top_k: Number of predictions to return.

    Returns:
        Dictionary containing predicted class label, confidence, 
        scientific name mapping, and top predictions.
    """
    model, class_names = load_inference_model()

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Target image file not found: {image_path}")

    # Load and preprocess image
    image = Image.open(image_path).convert("RGB")
    
    preprocess = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])
    
    crops = generate_inference_crops(image, size=224)
    batch_tensors = torch.stack([preprocess(c) for c in crops])
    
    # Use the device from load_inference_model (model already on device)
    device = _device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
    batch_tensors = batch_tensors.to(device)
    
    with torch.no_grad():
        outputs = model(batch_tensors)
        # Average the softmax probabilities across all multi-scale crops
        probabilities = torch.softmax(outputs, dim=1).mean(dim=0)
        
    # Get top predictions
    confidences, indices = torch.topk(probabilities, k=min(top_k, len(class_names)))
    
    predictions_list = []
    for score, idx in zip(confidences, indices):
        raw_name = class_names[idx.item()]
        mapped_name = map_class_name(raw_name)
        predictions_list.append({
            "name": mapped_name,
            "confidence": float(score.item())
        })
        
    top_match = predictions_list[0]
    
    return {
        "plant_name": top_match["name"],
        "confidence": top_match["confidence"],
        "top_predictions": predictions_list,
        "model_version": "mobilenetv3-v1.0.0"
    }

def main():
    """Entry point for CLI-based inference."""
    import argparse
    parser = argparse.ArgumentParser(description="Inference testing CLI")
    parser.add_argument("--image", required=True, help="Path to input image")
    args = parser.parse_args()
    
    try:
        results = predict(args.image)
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error executing inference: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
