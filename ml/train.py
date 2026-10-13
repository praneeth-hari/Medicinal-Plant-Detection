"""
train.py — Model Training Script
============================================================
Handles loading split datasets, PyTorch training, early stopping, 
metric evaluation, and saving checkpoints to plant_classifier.pth.
"""
from __future__ import annotations

import argparse
import os
import sys
import json
import random
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from sklearn.metrics import precision_recall_fscore_support, confusion_matrix

from pathlib import Path

# All paths are relative to this script's location (ml/)
_ML_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _ML_DIR.parent

sys.path.insert(0, str(_ROOT_DIR))

from ml.model import PlantClassifier
from ml.augment import BackgroundSwap

# Hyperparameters
BATCH_SIZE = 32
EPOCHS = 30
LEARNING_RATE = 1e-4
EARLY_STOPPING_PATIENCE = 7
MODEL_SAVE_PATH = str(_ROOT_DIR / "backend" / "data" / "models" / "plant_classifier.pth")
TRAINING_STATE_PATH = str(_ROOT_DIR / "backend" / "data" / "models" / "training_state.pth")
DATA_DIR = str(_ROOT_DIR / "data")

# ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

def evaluate_loader(model, loader, criterion, device, n_samples, seed=None):
    """Return (loss, accuracy) of ``model`` on ``loader``. ``seed`` fixes random augmentations."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    model.eval()
    total_loss, correct, total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            total_loss += criterion(outputs, labels).item() * images.size(0)
            correct += (outputs.argmax(1) == labels).sum().item()
            total += labels.size(0)
    return total_loss / n_samples, correct / total


def train_model(resume: bool = False, warm_start: bool = False, epochs: int = EPOCHS,
                lr: float = LEARNING_RATE, bg_prob: float = 0.7):
    global EPOCHS
    EPOCHS = epochs
    print("=" * 64)
    print("RESUMING PYTORCH MODEL TRAINING PIPELINE" if resume else "STARTING PYTORCH MODEL TRAINING PIPELINE")
    print("=" * 64)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Executing training on target device: {device}")
    
    # 1. Image Transformations
    # The raw photos have a strong per-class background bias (see ml/augment.py), so the
    # training set randomly swaps backgrounds and validation/test are also scored with
    # swapped backgrounds ("shifted") to measure real-world robustness.
    train_dir_for_pool = os.path.join(DATA_DIR, "train")
    train_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        BackgroundSwap(train_dir_for_pool, p=bg_prob),
        transforms.RandomResizedCrop(224, scale=(0.4, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomVerticalFlip(),
        transforms.RandomRotation(45),
        transforms.ColorJitter(brightness=0.35, contrast=0.35, saturation=0.35, hue=0.05),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    shifted_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        BackgroundSwap(train_dir_for_pool, p=1.0, seed=1234),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])

    # 2. Datasets & Loaders
    train_dir = os.path.join(DATA_DIR, "train")
    val_dir = os.path.join(DATA_DIR, "val")
    test_dir = os.path.join(DATA_DIR, "test")
    
    if not (os.path.exists(train_dir) and os.path.exists(val_dir)):
        print("Error: Train/Val split datasets not found. Run prepare_dataset first.")
        sys.exit(1)

    if not os.path.exists(test_dir):
        print("Error: Test split directory not found. Run prepare_dataset first.")
        sys.exit(1)
        
    train_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)
    val_dataset = datasets.ImageFolder(val_dir, transform=val_transforms)
    test_dataset = datasets.ImageFolder(test_dir, transform=val_transforms)
    val_shift_dataset = datasets.ImageFolder(val_dir, transform=shifted_transforms)
    test_shift_dataset = datasets.ImageFolder(test_dir, transform=shifted_transforms)
    
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    val_shift_loader = DataLoader(val_shift_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    test_shift_loader = DataLoader(test_shift_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)
    
    class_names = train_dataset.classes
    num_classes = len(class_names)
    print(f"Dataset summary:")
    print(f"  - Total Classes: {num_classes}")
    print(f"  - Class List: {class_names}")
    print(f"  - Train samples: {len(train_dataset)}")
    print(f"  - Val samples:   {len(val_dataset)}")
    print(f"  - Test samples:  {len(test_dataset)}")
    
    # Save the class names index mapping to a JSON file so inference can read it
    mapping_path = str(_ROOT_DIR / "backend" / "data" / "models" / "class_mapping.json")
    os.makedirs(os.path.dirname(mapping_path), exist_ok=True)
    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(class_names, f, indent=2)
    print(f"Class mapping index successfully saved to: {mapping_path}")
    
    # 3. Model, Criterion, Optimizer
    model = PlantClassifier(num_classes=num_classes, pretrained=True)
    model = model.to(device)

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.Adam(model.parameters(), lr=lr)

    if warm_start and os.path.exists(MODEL_SAVE_PATH):
        print(f"Warm-starting from existing weights: {MODEL_SAVE_PATH}")
        ckpt = torch.load(MODEL_SAVE_PATH, map_location=device, weights_only=True)
        model.load_state_dict(ckpt.get("model_state_dict", ckpt) if isinstance(ckpt, dict) else ckpt)

    # 4. Training Loop — initialise state (overwritten if resuming)
    best_val_loss = float("inf")
    best_val_acc = 0.0
    epochs_no_improve = 0
    start_epoch = 1
    history = {
        "train_loss": [], "train_acc": [],
        "val_loss": [], "val_acc": [],
        "val_shift_loss": [], "val_shift_acc": []
    }

    if resume:
        if os.path.exists(TRAINING_STATE_PATH):
            print(f"Loading full training state from: {TRAINING_STATE_PATH}")
            state = torch.load(TRAINING_STATE_PATH, map_location=device, weights_only=False)
            model.load_state_dict(state["model_state_dict"])
            optimizer.load_state_dict(state["optimizer_state_dict"])
            start_epoch = state["epoch"] + 1
            best_val_loss = state["best_val_loss"]
            best_val_acc = state["best_val_acc"]
            epochs_no_improve = state["epochs_no_improve"]
            history = state["history"]
            print(f"Resuming from epoch {start_epoch} | Best val loss so far: {best_val_loss:.4f}")
        elif os.path.exists(MODEL_SAVE_PATH):
            print(f"No full training state found. Loading model weights from: {MODEL_SAVE_PATH}")
            ckpt = torch.load(MODEL_SAVE_PATH, map_location=device, weights_only=True)
            model.load_state_dict(ckpt.get("model_state_dict", ckpt) if isinstance(ckpt, dict) else ckpt)
            print("Warm-starting from saved weights; optimizer state reset.")
        else:
            print("Warning: --resume specified but no checkpoint found. Starting from scratch.")

    remaining_epochs = EPOCHS - (start_epoch - 1)
    if remaining_epochs <= 0:
        print(f"Already completed {EPOCHS} epochs. Increase EPOCHS to train further.")
        sys.exit(0)

    start_time = time.time()

    for epoch in range(start_epoch, EPOCHS + 1):
        epoch_start = time.time()
        
        # Training pass
        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        
        total_batches = len(train_loader)
        for batch_idx, (images, labels) in enumerate(train_loader, start=1):
            images, labels = images.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

            if batch_idx % 25 == 0 or batch_idx == total_batches:
                batch_acc = (predicted == labels).sum().item() / labels.size(0)
                print(f"  [Epoch {epoch}/{EPOCHS}] Batch {batch_idx:3d}/{total_batches} | "
                      f"Loss: {loss.item():.4f} | Batch Acc: {batch_acc*100:.1f}%", flush=True)
            
        epoch_train_loss = running_loss / len(train_dataset)
        epoch_train_acc = correct_train / total_train
        
        # Validation: original photos + background-swapped photos (robustness)
        epoch_val_loss, epoch_val_acc = evaluate_loader(model, val_loader, criterion, device, len(val_dataset))
        shift_loss, shift_acc = evaluate_loader(
            model, val_shift_loader, criterion, device, len(val_shift_dataset), seed=1234)
        # Model selection uses the average so a background-biased model is not preferred
        select_loss = (epoch_val_loss + shift_loss) / 2

        history["train_loss"].append(epoch_train_loss)
        history["train_acc"].append(epoch_train_acc)
        history["val_loss"].append(epoch_val_loss)
        history["val_acc"].append(epoch_val_acc)
        history["val_shift_loss"].append(shift_loss)
        history["val_shift_acc"].append(shift_acc)
        
        epoch_duration = time.time() - epoch_start
        print(f"Epoch {epoch:02d}/{EPOCHS:02d} | "
              f"Train Loss: {epoch_train_loss:.4f} | Train Acc: {epoch_train_acc:.4f} | "
              f"Val Acc: {epoch_val_acc:.4f} | Val(shifted) Acc: {shift_acc:.4f} | Sel Loss: {select_loss:.4f} | "
              f"Duration: {epoch_duration:.1f}s")
              
        # Model saving and early stopping check
        if select_loss < best_val_loss:
            best_val_loss = select_loss
            best_val_acc = epoch_val_acc
            epochs_no_improve = 0
            os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)
            # Save inference-ready weights (plain state_dict)
            model.save_checkpoint(MODEL_SAVE_PATH)
            print(f"  --> Best weights checkpoint saved to: {MODEL_SAVE_PATH}")
            # Save full training state for resuming
            torch.save({
                "epoch": epoch,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "best_val_loss": best_val_loss,
                "best_val_acc": best_val_acc,
                "epochs_no_improve": epochs_no_improve,
                "history": history,
            }, TRAINING_STATE_PATH)
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= EARLY_STOPPING_PATIENCE:
                print(f"Early stopping triggered after {epoch} epochs. Training finished.")
                break
                
    total_training_duration = time.time() - start_time
    print(f"\nTraining completed in {total_training_duration:.1f}s. Evaluating best model on test set...")
    
    # 5. Final Evaluation on Test Set
    # Load the best checkpoint to evaluate
    best_model = PlantClassifier.load_checkpoint(MODEL_SAVE_PATH, num_classes=num_classes)
    best_model = best_model.to(device)
    best_model.eval()
    
    all_preds = []
    all_labels = []
    
    inference_times = []
    
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(device)
            
            # Record individual inference latencies
            for i in range(images.size(0)):
                single_img = images[i].unsqueeze(0)
                inf_start = time.time()
                outputs = best_model(single_img)
                inference_times.append(time.time() - inf_start)
                
                _, predicted = torch.max(outputs, 1)
                all_preds.append(predicted.item())
                
            all_labels.extend(labels.numpy())
            
    # Calculate performance metrics
    precision, recall, f1, _ = precision_recall_fscore_support(all_labels, all_preds, average='macro')
    cm = confusion_matrix(all_labels, all_preds)
    
    test_correct = sum(1 for p, l in zip(all_preds, all_labels) if p == l)
    test_accuracy = test_correct / len(all_labels)
    avg_inference_latency = sum(inference_times) / len(inference_times)
    _, test_shift_acc = evaluate_loader(
        best_model, test_shift_loader, criterion, device, len(test_shift_dataset), seed=1234)
    
    print("\n" + "=" * 64)
    print("FINAL EVALUATION METRICS REPORT")
    print("=" * 64)
    print(f"Best Validation Accuracy: {best_val_acc:.4f}")
    print(f"Test Accuracy:           {test_accuracy:.4f} ({test_correct}/{len(all_labels)})")
    print(f"Test Acc (backgrounds swapped): {test_shift_acc:.4f}")
    print(f"Precision (Macro):        {precision:.4f}")
    print(f"Recall (Macro):           {recall:.4f}")
    print(f"F1 Score (Macro):         {f1:.4f}")
    print(f"Average Inference Time:   {avg_inference_latency * 1000:.2f} ms")
    
    # Generate structured report file
    report = {
        "dataset_size": len(train_dataset) + len(val_dataset) + len(test_dataset),
        "classes_used": class_names,
        "split_counts": {
            "train": len(train_dataset),
            "val": len(val_dataset),
            "test": len(test_dataset)
        },
        "model_architecture": "MobileNetV3-Small",
        "best_val_accuracy": round(best_val_acc, 4),
        "test_accuracy": round(test_accuracy, 4),
        "test_accuracy_background_shifted": round(test_shift_acc, 4),
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1_score": round(f1, 4),
        "average_inference_time_ms": round(avg_inference_latency * 1000, 2),
        "confusion_matrix": cm.tolist()
    }
    
    report_path = str(_ROOT_DIR / "backend" / "data" / "training_metrics_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Final training evaluation report written directly to: {report_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the medicinal plant classifier.")
    parser.add_argument("--resume", action="store_true", help="Resume training from the last saved checkpoint.")
    parser.add_argument("--warm-start", action="store_true", help="Start from the saved weights with a fresh optimizer (fine-tune).")
    parser.add_argument("--epochs", type=int, default=EPOCHS, help="Maximum number of epochs.")
    parser.add_argument("--lr", type=float, default=LEARNING_RATE, help="Learning rate.")
    parser.add_argument("--bg-prob", type=float, default=0.7, help="Probability of background-swap augmentation.")
    args = parser.parse_args()
    train_model(resume=args.resume, warm_start=args.warm_start, epochs=args.epochs,
                lr=args.lr, bg_prob=args.bg_prob)
