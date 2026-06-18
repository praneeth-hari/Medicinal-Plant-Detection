"""
Plant Endpoints
===============

CRUD API endpoints for medicinal plant records.

Routes:
    GET    /             — List all plants (paginated).
    GET    /search       — Search plants by name.
    GET    /{plant_id}   — Retrieve a single plant by ID.
    POST   /             — Create a new plant record.
    PUT    /{plant_id}   — Update an existing plant.
    DELETE /{plant_id}   — Delete a plant record.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query, status

from api.deps import get_plant_service
from schemas.plant import PlantCreate, PlantListResponse, PlantResponse, PlantUpdate
from services.plant_service import PlantService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=list[PlantResponse],
    summary="List plants",
    description="Retrieve a paginated list of all medicinal plants.",
)
async def list_plants(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    service: PlantService = Depends(get_plant_service),
) -> list[PlantResponse]:
    """Return a paginated list of plants.

    Args:
        skip: Pagination offset.
        limit: Page size.
        service: Injected ``PlantService``.

    Returns:
        List of ``PlantResponse`` objects.
    """
    plants = await service.list_plants(skip=skip, limit=limit)
    return [PlantResponse.model_validate(p) for p in plants]


@router.get(
    "/search",
    response_model=list[PlantResponse],
    summary="Search plants",
    description="Search plants by common or scientific name.",
)
async def search_plants(
    q: str = Query(
        ..., min_length=1, max_length=200,
        description="Search query (partial match on name)",
    ),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    service: PlantService = Depends(get_plant_service),
) -> list[PlantResponse]:
    """Search plants by common or scientific name.

    Args:
        q: Search term (case-insensitive, partial match).
        skip: Pagination offset.
        limit: Page size.
        service: Injected ``PlantService``.

    Returns:
        Matching ``PlantResponse`` objects.
    """
    plants = await service.search_plants(q, skip=skip, limit=limit)
    return [PlantResponse.model_validate(p) for p in plants]


@router.get(
    "/{plant_id}",
    response_model=PlantResponse,
    summary="Get plant",
    description="Retrieve a single plant by its ID.",
)
async def get_plant(
    plant_id: int,
    service: PlantService = Depends(get_plant_service),
) -> PlantResponse:
    """Retrieve a single plant record.

    Args:
        plant_id: Plant primary key.
        service: Injected ``PlantService``.

    Returns:
        ``PlantResponse`` if found.

    Raises:
        NotFoundException: 404 if the plant does not exist.
    """
    plant = await service.get_plant(plant_id)
    return PlantResponse.model_validate(plant)


@router.post(
    "/",
    response_model=PlantResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create plant",
    description="Add a new medicinal plant to the database.",
)
async def create_plant(
    plant_in: PlantCreate,
    service: PlantService = Depends(get_plant_service),
) -> PlantResponse:
    """Create a new plant record.

    Args:
        plant_in: Validated creation payload.
        service: Injected ``PlantService``.

    Returns:
        Newly created ``PlantResponse``.

    Raises:
        AlreadyExistsException: 409 if scientific_name already exists.
    """
    plant = await service.create_plant(plant_in)
    return PlantResponse.model_validate(plant)


@router.put(
    "/{plant_id}",
    response_model=PlantResponse,
    summary="Update plant",
    description="Update an existing medicinal plant record.",
)
async def update_plant(
    plant_id: int,
    plant_in: PlantUpdate,
    service: PlantService = Depends(get_plant_service),
) -> PlantResponse:
    """Update an existing plant record.

    Args:
        plant_id: Plant primary key.
        plant_in: Partial update payload.
        service: Injected ``PlantService``.

    Returns:
        Updated ``PlantResponse``.

    Raises:
        NotFoundException: 404 if the plant does not exist.
        AlreadyExistsException: 409 if scientific_name collides.
    """
    plant = await service.update_plant(plant_id, plant_in)
    return PlantResponse.model_validate(plant)


@router.delete(
    "/{plant_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete plant",
    description="Delete a medicinal plant record.",
)
async def delete_plant(
    plant_id: int,
    service: PlantService = Depends(get_plant_service),
) -> None:
    """Delete a plant record.

    Args:
        plant_id: Plant primary key.
        service: Injected ``PlantService``.

    Raises:
        NotFoundException: 404 if the plant does not exist.
    """
    await service.delete_plant(plant_id)
