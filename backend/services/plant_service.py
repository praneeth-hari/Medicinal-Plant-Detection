"""
Plant Service
=============

Business-logic layer for plant CRUD and search operations.
Delegates data access to ``PlantRepository``.
"""

from __future__ import annotations

from typing import Optional, Sequence

from repositories.plant_repository import PlantRepository
from schemas.plant import PlantCreate, PlantResponse, PlantUpdate


class PlantService:
    """Service encapsulating business rules for plant management.

    Args:
        repository: Injected ``PlantRepository`` instance.
    """

    def __init__(self, repository: PlantRepository) -> None:
        """Initialise the service with a plant repository.

        Args:
            repository: Data-access dependency.
        """
        self.repository = repository

    async def get_plant(self, plant_id: int) -> Optional[PlantResponse]:
        """Retrieve a single plant by ID.

        Args:
            plant_id: Primary key.

        Returns:
            ``PlantResponse`` or ``None``.
        """
        raise NotImplementedError("Not yet implemented")

    async def list_plants(self, *, skip: int = 0, limit: int = 100) -> Sequence[PlantResponse]:
        """Return a paginated list of all plants.

        Args:
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``PlantResponse`` objects.
        """
        raise NotImplementedError("Not yet implemented")

    async def create_plant(self, data: PlantCreate) -> PlantResponse:
        """Create a new plant record.

        Args:
            data: Validated creation payload.

        Returns:
            Newly created ``PlantResponse``.
        """
        raise NotImplementedError("Not yet implemented")

    async def update_plant(self, plant_id: int, data: PlantUpdate) -> Optional[PlantResponse]:
        """Update an existing plant.

        Args:
            plant_id: Primary key.
            data: Partial update payload.

        Returns:
            Updated ``PlantResponse`` or ``None`` if not found.
        """
        raise NotImplementedError("Not yet implemented")

    async def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant by ID.

        Args:
            plant_id: Primary key.

        Returns:
            ``True`` if successfully deleted.
        """
        raise NotImplementedError("Not yet implemented")

    async def search_plants(self, query: str, *, limit: int = 20) -> Sequence[PlantResponse]:
        """Search plants by name.

        Args:
            query: Search term.
            limit: Max results.

        Returns:
            Matching ``PlantResponse`` objects.
        """
        raise NotImplementedError("Not yet implemented")
