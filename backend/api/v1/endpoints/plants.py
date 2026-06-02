"""
Plant Endpoints
===============

CRUD API endpoints for medicinal plant records.

Routes:
    GET    /           — List all plants (paginated).
    GET    /{plant_id} — Retrieve a single plant by ID.
    POST   /           — Create a new plant record.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.deps import get_plant_service
from schemas.plant import PlantCreate, PlantResponse
from services.plant_service import PlantService

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
    raise NotImplementedError("Not yet implemented")


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
        HTTPException: 404 if the plant does not exist.
    """
    raise NotImplementedError("Not yet implemented")


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
    """
    raise NotImplementedError("Not yet implemented")
