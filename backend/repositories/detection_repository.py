"""
Detection Repository
====================

Data-access layer for ``DetectionResult`` entities.  Inherits generic
CRUD from ``BaseRepository`` and adds detection-specific queries
for user history and plant-based lookups.
"""
from __future__ import annotations

import logging
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from models.detection import DetectionResult
from repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class DetectionRepository(BaseRepository[DetectionResult]):
    """Repository for plant detection results.

    Inherits generic CRUD from ``BaseRepository`` and adds
    queries for user-scoped and plant-scoped lookups.

    Attributes:
        model: The ``DetectionResult`` ORM class.
    """

    model = DetectionResult

    def __init__(self, session: AsyncSession) -> None:
        """Initialise with an async database session.

        Args:
            session: SQLAlchemy ``AsyncSession``.
        """
        super().__init__(session)

    # ---- Detection-specific queries ----

    async def get_with_plant(self, id: int) -> Optional[DetectionResult]:
        """Retrieve a detection result by primary key, eagerly loading the plant.

        Args:
            id: DetectionResult primary key.

        Returns:
            ``DetectionResult`` instance with plant relationship loaded,
            or ``None`` if not found.
        """
        stmt = (
            select(DetectionResult)
            .options(joinedload(DetectionResult.plant))
            .where(DetectionResult.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def get_by_user(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[DetectionResult]:
        """Retrieve all detection results for a given user.

        Results are returned in reverse chronological order with
        the plant relationship eagerly loaded.

        Args:
            user_id: User's primary key.
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``DetectionResult`` instances.
        """
        stmt = (
            select(DetectionResult)
            .options(joinedload(DetectionResult.plant))
            .where(DetectionResult.user_id == user_id)
            .order_by(DetectionResult.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_by_plant(
        self,
        plant_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[DetectionResult]:
        """Retrieve all detection results associated with a specific plant.

        Args:
            plant_id: Plant's primary key.
            skip: Offset.
            limit: Max results.

        Returns:
            Sequence of ``DetectionResult`` instances.
        """
        stmt = (
            select(DetectionResult)
            .options(joinedload(DetectionResult.plant))
            .where(DetectionResult.plant_id == plant_id)
            .order_by(DetectionResult.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()
