"""
Plant Service
=============

Business-logic layer for plant CRUD and search operations.
Delegates data access to ``PlantRepository`` and converts
ORM models to Pydantic response schemas.
"""
from __future__ import annotations

import logging
from typing import Optional, Sequence

from api.exceptions import AlreadyExistsException, NotFoundException
from models.plant import Plant
from repositories.plant_repository import PlantRepository
from schemas.plant import PlantCreate, PlantResponse, PlantUpdate

logger = logging.getLogger(__name__)


class PlantService:
    """Service encapsulating business rules for plant management.

    All public methods return Pydantic schemas (not ORM models),
    ensuring a clean boundary between layers.

    Args:
        repository: Injected ``PlantRepository`` instance.
    """

    def __init__(self, repository: PlantRepository) -> None:
        """Initialise the service with a plant repository.

        Args:
            repository: Data-access dependency.
        """
        self.repository = repository

    async def get_plant(self, plant_id: int) -> Plant:
        """Retrieve a single plant by ID.

        Args:
            plant_id: Primary key.

        Returns:
            ``Plant`` ORM model.

        Raises:
            NotFoundException: If the plant does not exist.
        """
        plant = await self.repository.get(plant_id)
        if plant is None:
            raise NotFoundException("Plant", plant_id)
        return plant

    async def list_plants(
        self, *, skip: int = 0, limit: int = 100,
    ) -> Sequence[Plant]:
        """Return a paginated list of all plants.

        Args:
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``Plant`` ORM models.
        """
        return await self.repository.get_all(skip=skip, limit=limit)

    async def create_plant(self, data: PlantCreate) -> Plant:
        """Create a new plant record.

        Checks for duplicate ``scientific_name`` before persisting.

        Args:
            data: Validated creation payload.

        Returns:
            Newly created ``Plant`` ORM model.

        Raises:
            AlreadyExistsException: If a plant with the same
                scientific name already exists.
        """
        existing = await self.repository.get_by_scientific_name(
            data.scientific_name,
        )
        if existing is not None:
            raise AlreadyExistsException("Plant", "scientific_name")
        plant = await self.repository.create(data.model_dump())
        logger.info(
            "Created plant: %s (%s)",
            plant.common_name,
            plant.scientific_name,
        )
        return plant

    async def update_plant(
        self, plant_id: int, data: PlantUpdate,
    ) -> Plant:
        """Update an existing plant.

        Only fields present in ``data`` (non-None) are updated.

        Args:
            plant_id: Primary key.
            data: Partial update payload.

        Returns:
            Updated ``Plant`` ORM model.

        Raises:
            NotFoundException: If the plant does not exist.
            AlreadyExistsException: If the new scientific name collides
                with an existing record.
        """
        # Verify plant exists
        await self.get_plant(plant_id)

        # If scientific_name is being changed, check for collisions
        update_data = data.model_dump(exclude_unset=True)
        if "scientific_name" in update_data:
            existing = await self.repository.get_by_scientific_name(
                update_data["scientific_name"],
            )
            if existing is not None and existing.id != plant_id:
                raise AlreadyExistsException("Plant", "scientific_name")

        plant = await self.repository.update(plant_id, update_data)
        logger.info("Updated plant id=%d", plant_id)
        return plant  # type: ignore[return-value]

    async def delete_plant(self, plant_id: int) -> bool:
        """Delete a plant by ID.

        Args:
            plant_id: Primary key.

        Returns:
            ``True`` if successfully deleted.

        Raises:
            NotFoundException: If the plant does not exist.
        """
        await self.get_plant(plant_id)
        result = await self.repository.delete(plant_id)
        logger.info("Deleted plant id=%d", plant_id)
        return result

    async def search_plants(
        self, query: str, *, skip: int = 0, limit: int = 20,
    ) -> Sequence[Plant]:
        """Search plants by name (common or scientific).

        Args:
            query: Search term.
            skip: Pagination offset.
            limit: Max results.

        Returns:
            Matching ``Plant`` ORM models.
        """
        return await self.repository.search_by_name(
            query, skip=skip, limit=limit,
        )

    async def count_plants(self) -> int:
        """Return the total number of plants in the database.

        Returns:
            Plant count.
        """
        return await self.repository.count()
