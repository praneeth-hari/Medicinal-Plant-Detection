"""
test_detection.py — Tests for the Detection API endpoints.
============================================================
Covers image upload, plant detection, and detection history.
"""

import pytest


class TestDetectionAPI:
    """Test suite for /api/v1/detect endpoints."""

    def test_detect_plant_from_image(self):
        """POST /detect/image should accept an image and return a prediction."""
        # TODO: Implement test
        pass

    def test_detect_invalid_file_type_returns_400(self):
        """POST /detect/image with non-image file should return 400."""
        # TODO: Implement test
        pass

    def test_get_detection_history(self):
        """GET /detect/history should return the user's detection history."""
        # TODO: Implement test
        pass

    def test_get_detection_by_id(self):
        """GET /detect/{id} should return details of a specific detection."""
        # TODO: Implement test
        pass

    def test_detect_requires_authentication(self):
        """POST /detect/image without auth should return 401."""
        # TODO: Implement test
        pass
