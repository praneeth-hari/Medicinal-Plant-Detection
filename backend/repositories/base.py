"""
Base Repository
===============

Generic base repository providing concrete CRUD implementations
using SQLAlchemy async sessions.  Concrete repositories inherit
from this class and set the ``model`` attribute.

Usage::

    class PlantRepository(BaseRepository[Plant]):
        model = Plant
"""
from __future__ import annotations

import logging
from typing import Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Base

logger = logging.getLogger(__name__)

# Generic type variable bound to our ORM base class.
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic base repository providing standard CRUD operations.

    Subclasses must set ``model`` to the concrete SQLAlchemy model class
    they manage and may override or extend any of the methods below.

    Attributes:
        model: The SQLAlchemy ORM model class managed by this repository.
        session: The active async database session.

    Args:
        session: An active ``AsyncSession`` for database access.
    """

    model: Type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        """Initialise the repository with an async database session.

        Args:
            session: SQLAlchemy async session provided via dependency injection.
        """
        self.session = session

    async def get(self, id: int) -> Optional[ModelType]:
        """Retrieve a single entity by its primary key.

        Args:
            id: The primary-key value.

        Returns:
            The model instance, or ``None`` if not found.
        """
        result = await self.session.get(self.model, id)
        return result

    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieve a paginated list of entities.

        Args:
            skip: Number of rows to skip (offset).
            limit: Maximum number of rows to return.

        Returns:
            A sequence of model instances.
        """
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj_in: dict) -> ModelType:
        """Persist a new entity.

        Args:
            obj_in: Dictionary of column values for the new row.

        Returns:
            The newly created model instance (with server-generated fields).
        """
        db_obj = self.model(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        logger.debug("Created %s(id=%s)", self.model.__name__, db_obj.id)
        return db_obj

    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """Update an existing entity.

        Args:
            id: Primary key of the entity to update.
            obj_in: Dictionary of column values to update.  Only keys
                    present in the dict are modified; ``None`` values
                    are explicitly set.

        Returns:
            The updated model instance, or ``None`` if not found.
        """
        db_obj = await self.get(id)
        if db_obj is None:
            return None
        for key, value in obj_in.items():
            setattr(db_obj, key, value)
        await self.session.flush()
        await self.session.refresh(db_obj)
        logger.debug("Updated %s(id=%s)", self.model.__name__, id)
        return db_obj

    async def delete(self, id: int) -> bool:
        """Delete an entity by primary key.

        Args:
            id: Primary key of the entity to remove.

        Returns:
            ``True`` if a row was deleted, ``False`` otherwise.
        """
        db_obj = await self.get(id)
        if db_obj is None:
            return False
        await self.session.delete(db_obj)
        await self.session.flush()
        logger.debug("Deleted %s(id=%s)", self.model.__name__, id)
        return True

    async def count(self) -> int:
        """Return the total number of rows for this model.

        Returns:
            Row count as an integer.
        """
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()
