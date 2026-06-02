"""
Plant Repository
================

Data-access layer for ``Plant`` entities.  Extends the generic
``BaseRepository`` with plant-specific query methods.
"""

from __future__ import annotations

from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from models.plant import Plant
from repositories.base import BaseRepository


class PlantRepository(BaseRepository[Plant]):
    """Repository handling all database operations for plants.

    Attributes:
        model: The ``Plant`` ORM class managed by this repository.
    """

    model = Plant

    def __init__(self, session: AsyncSession) -> None:
        """Initialise with an async database session.

        Args:
            session: SQLAlchemy ``AsyncSession``.
        """
        super().__init__(session)

    # ---- BaseRepository CRUD stubs ----

    async def get(self, id: int) -> Optional[Plant]:
        """Retrieve a plant by its primary key.

        Args:
            id: Plant primary key.

        Returns:
            ``Plant`` instance or ``None``.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[Plant]:
        """Retrieve a paginated list of plants.

        Args:
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``Plant`` instances.
        """
        raise NotImplementedError("Not yet implemented")

    async def create(self, obj_in: dict) -> Plant:
        """Create a new plant record.

        Args:
            obj_in: Column data.

        Returns:
            Newly created ``Plant``.
        """
        raise NotImplementedError("Not yet implemented")

    async def update(self, id: int, obj_in: dict) -> Optional[Plant]:
        """Update an existing plant record.

        Args:
            id: Plant primary key.
            obj_in: Fields to update.

        Returns:
            Updated ``Plant`` or ``None``.
        """
        raise NotImplementedError("Not yet implemented")

    async def delete(self, id: int) -> bool:
        """Delete a plant record.

        Args:
            id: Plant primary key.

        Returns:
            ``True`` if deleted.
        """
        raise NotImplementedError("Not yet implemented")

    # ---- Plant-specific queries ----

    async def search_by_name(self, query: str, *, limit: int = 20) -> Sequence[Plant]:
        """Search plants by common or scientific name (partial match).

        Args:
            query: Search term.
            limit: Maximum results to return.

        Returns:
            Matching ``Plant`` instances.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_by_scientific_name(self, scientific_name: str) -> Optional[Plant]:
        """Retrieve a plant by its exact scientific name.

        Args:
            scientific_name: Binomial nomenclature string.

        Returns:
            ``Plant`` instance or ``None``.
        """
        raise NotImplementedError("Not yet implemented")
