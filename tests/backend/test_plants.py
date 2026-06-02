"""
test_plants.py — Tests for the Plants API endpoints.
============================================================
Covers CRUD operations for medicinal plant records.
"""

import pytest


class TestPlantsAPI:
    """Test suite for /api/v1/plants endpoints."""

    def test_list_plants(self):
        """GET /plants should return a list of all plants."""
        # TODO: Implement test
        pass

    def test_get_plant_by_id(self):
        """GET /plants/{id} should return a single plant's details."""
        # TODO: Implement test
        pass

    def test_create_plant(self):
        """POST /plants should create a new plant record (admin only)."""
        # TODO: Implement test
        pass

    def test_update_plant(self):
        """PUT /plants/{id} should update an existing plant record."""
        # TODO: Implement test
        pass

    def test_delete_plant(self):
        """DELETE /plants/{id} should remove a plant record."""
        # TODO: Implement test
        pass

    def test_get_nonexistent_plant_returns_404(self):
        """GET /plants/{id} with invalid ID should return 404."""
        # TODO: Implement test
        pass
