"""
model.py — PyTorch Model Architecture Definition
============================================================
This module defines the neural network architecture for
medicinal plant image classification.
"""
from __future__ import annotations

import torch
import torch.nn as nn
from torchvision.models import mobilenet_v3_small, MobileNet_V3_Small_Weights

class PlantClassifier(nn.Module):
    """
    PyTorch model for medicinal plant classification.
    Uses pretrained MobileNetV3-Small backbone with a customized classification head.
    """

    def __init__(self, num_classes: int = 14, model_name: str = "mobilenet_v3", pretrained: bool = True):
        """
        Initialize the plant classifier.

        Args:
            num_classes: Number of plant species to classify.
            model_name: Name of the backbone architecture (defaults to mobilenet_v3).
            pretrained: Whether to use pretrained ImageNet weights.
        """
        super().__init__()
        self.num_classes = num_classes
        self.model_name = model_name

        if pretrained:
            weights = MobileNet_V3_Small_Weights.DEFAULT
            self.backbone = mobilenet_v3_small(weights=weights)
        else:
            self.backbone = mobilenet_v3_small(weights=None)

        # MobileNetV3-Small classifier has structure:
        # (classifier): Sequential(
        #   (0): Linear(in_features=576, out_features=1024, bias=True)
        #   (1): Hardswish()
        #   (2): Dropout(p=0.2, inplace=True)
        #   (3): Linear(in_features=1024, out_features=1000, bias=True)
        # )
        in_features = self.backbone.classifier[0].in_features
        hidden_features = self.backbone.classifier[0].out_features

        # Replace the final layer sequence
        self.backbone.classifier = nn.Sequential(
            nn.Linear(in_features, hidden_features),
            nn.Hardswish(),
            nn.Dropout(p=0.2, inplace=True),
            nn.Linear(hidden_features, num_classes)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Forward pass.
        
        Args:
            x: Input image tensor of shape (Batch, 3, 224, 224).
            
        Returns:
            Logits of shape (Batch, num_classes).
        """
        return self.backbone(x)

    def save_checkpoint(self, checkpoint_path: str):
        """Save the model state dictionary to disk."""
        torch.save(self.state_dict(), checkpoint_path)

    @staticmethod
    def load_checkpoint(checkpoint_path: str, num_classes: int = 14) -> PlantClassifier:
        """
        Load model weights from a checkpoint file.
        
        Args:
            checkpoint_path: Path to the .pth state dictionary.
            num_classes: Number of target classes.
            
        Returns:
            An instantiated PlantClassifier with loaded weights.
        """
        model = PlantClassifier(num_classes=num_classes, pretrained=False)
        # Load map_location='cpu' since inference and local runs happen on CPU
        state_dict = torch.load(checkpoint_path, map_location=torch.device('cpu'))
        model.load_state_dict(state_dict)
        model.eval()
        return model
