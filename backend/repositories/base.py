"""
Base Repository
===============

Abstract, generic base repository that defines the standard CRUD
interface every concrete repository must implement.  Uses Python
generics so that type checkers can infer the model type downstream.

Usage::

    class PlantRepository(BaseRepository[Plant]):
        ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, Optional, Sequence, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from models.base import Base

# Generic type variable bound to our ORM base class.
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(ABC, Generic[ModelType]):
    """Abstract base repository providing a generic CRUD contract.

    Subclasses must set ``model`` to the concrete SQLAlchemy model class
    they manage and may override or extend any of the methods below.

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

    @abstractmethod
    async def get(self, id: int) -> Optional[ModelType]:
        """Retrieve a single entity by its primary key.

        Args:
            id: The primary-key value.

        Returns:
            The model instance, or ``None`` if not found.
        """
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    async def get_all(self, *, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Retrieve a paginated list of entities.

        Args:
            skip: Number of rows to skip (offset).
            limit: Maximum number of rows to return.

        Returns:
            A sequence of model instances.
        """
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    async def create(self, obj_in: dict) -> ModelType:
        """Persist a new entity.

        Args:
            obj_in: Dictionary of column values for the new row.

        Returns:
            The newly created model instance (with server-generated fields).
        """
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    async def update(self, id: int, obj_in: dict) -> Optional[ModelType]:
        """Update an existing entity.

        Args:
            id: Primary key of the entity to update.
            obj_in: Dictionary of column values to update.

        Returns:
            The updated model instance, or ``None`` if not found.
        """
        raise NotImplementedError("Not yet implemented")

    @abstractmethod
    async def delete(self, id: int) -> bool:
        """Delete an entity by primary key.

        Args:
            id: Primary key of the entity to remove.

        Returns:
            ``True`` if a row was deleted, ``False`` otherwise.
        """
        raise NotImplementedError("Not yet implemented")
