"""
model.py — PyTorch Model Architecture Definition
============================================================
This module defines the neural network architecture for
medicinal plant image classification.

Responsibilities:
    - Define the model class (e.g., fine-tuned ResNet, EfficientNet)
    - Support loading pretrained backbones from torchvision
    - Customize the classifier head for the target number of classes
    - Provide utilities for loading/saving model checkpoints
"""

# TODO: Implement model architecture


class PlantClassifier:
    """
    PyTorch model for medicinal plant classification.

    This will typically be a pretrained CNN backbone (e.g., ResNet50,
    EfficientNet-B0) with a custom classification head fine-tuned
    on the medicinal plant dataset.
    """

    def __init__(self, num_classes: int, model_name: str = "resnet50", pretrained: bool = True):
        """
        Initialize the plant classifier.

        Args:
            num_classes: Number of plant species to classify.
            model_name: Name of the backbone architecture.
            pretrained: Whether to use pretrained ImageNet weights.
        """
        raise NotImplementedError("Model architecture not yet implemented.")

    def forward(self, x):
        """Forward pass."""
        raise NotImplementedError

    @staticmethod
    def load_checkpoint(checkpoint_path: str):
        """Load model weights from a checkpoint file."""
        raise NotImplementedError
