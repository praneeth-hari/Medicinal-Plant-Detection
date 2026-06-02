"""
config.py — ML Hyperparameter Configuration
============================================================
Central configuration for model training hyperparameters.
Modify these values to tune model performance.
"""

# ----- Training Hyperparameters -----
LEARNING_RATE = 1e-4          # Initial learning rate for the optimizer
BATCH_SIZE = 32               # Number of samples per training batch
EPOCHS = 50                   # Maximum number of training epochs
WEIGHT_DECAY = 1e-5           # L2 regularization weight decay

# ----- Image Configuration -----
IMAGE_SIZE = 224              # Input image resolution (IMAGE_SIZE x IMAGE_SIZE)
NUM_CHANNELS = 3              # Number of image channels (RGB)

# ----- Model Configuration -----
NUM_CLASSES = 40              # Number of medicinal plant species to classify
MODEL_NAME = "resnet50"       # Backbone architecture (resnet50, efficientnet_b0, etc.)
PRETRAINED = True             # Use ImageNet-pretrained weights

# ----- Data Paths -----
DATA_DIR = "data/raw"                 # Raw dataset directory
PROCESSED_DIR = "data/processed"      # Preprocessed dataset directory
MODEL_SAVE_DIR = "data/models"        # Directory to save trained model checkpoints

# ----- Experiment Tracking -----
WANDB_PROJECT = "medicinal-plant-detection"   # Weights & Biases project name
WANDB_ENABLED = False                         # Enable W&B logging
