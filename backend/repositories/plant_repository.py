"""
Plant Repository
================

Data-access layer for ``Plant`` entities.  Extends the generic
``BaseRepository`` with plant-specific query methods such as
name search and scientific-name lookup.
"""
from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy import or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.plant import Plant
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class PlantRepository(BaseRepository[Plant]):
    """Repository handling all database operations for plants.

    Inherits generic CRUD from ``BaseRepository`` and adds
    plant-specific queries.

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

    # ---- Plant-specific queries ----

    async def search_by_name(
        self, query: str, *, skip: int = 0, limit: int = 20,
    ) -> Sequence[Plant]:
        """Search plants by common or scientific name (case-insensitive partial match).

        Uses SQL ``ILIKE`` (via ``.ilike()``) so the search is
        case-insensitive and supports partial matches.

        Args:
            query: Search term (e.g., ``"tul"`` matches ``"Tulsi"``).
            skip: Pagination offset.
            limit: Maximum results to return.

        Returns:
            Matching ``Plant`` instances ordered by common name.
        """
        pattern = f"%{query}%"
        stmt = (
            select(Plant)
            .where(
                or_(
                    Plant.common_name.ilike(pattern),
                    Plant.scientific_name.ilike(pattern),
                )
            )
            .order_by(Plant.common_name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_scientific_name(self, scientific_name: str) -> Optional[Plant]:
        """Retrieve a plant by its exact scientific name.

        Args:
            scientific_name: Binomial nomenclature string (case-insensitive).

        Returns:
            ``Plant`` instance or ``None``.
        """
        stmt = select(Plant).where(
            func.lower(Plant.scientific_name) == scientific_name.lower()
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_family(
        self, family: str, *, skip: int = 0, limit: int = 100,
    ) -> Sequence[Plant]:
        """Retrieve plants belonging to a botanical family.

        Args:
            family: Family name (e.g., ``"Lamiaceae"``).
            skip: Pagination offset.
            limit: Maximum results to return.

        Returns:
            Matching ``Plant`` instances.
        """
        stmt = (
            select(Plant)
            .where(func.lower(Plant.family) == family.lower())
            .order_by(Plant.common_name)
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
