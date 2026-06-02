"""
Detection Endpoints
===================

API endpoints for plant image detection and detection history.

Routes:
    POST  /              — Upload an image for plant detection.
    GET   /history       — Retrieve detection history for the current user.
    GET   /{detection_id} — Retrieve a specific detection result.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status

from api.deps import get_current_user, get_detection_service
from schemas.detection import DetectionResponse
from schemas.user import TokenData
from services.detection_service import DetectionService

router = APIRouter()


@router.post(
    "/",
    response_model=DetectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Detect plant",
    description="Upload an image and run the plant classification model.",
)
async def detect_plant(
    image: UploadFile = File(..., description="Plant image to classify"),
    current_user: TokenData = Depends(get_current_user),
    service: DetectionService = Depends(get_detection_service),
) -> DetectionResponse:
    """Upload an image for plant detection.

    Reads the uploaded file bytes, delegates to ``DetectionService``
    for model inference, and returns the prediction result.

    Args:
        image: Uploaded image file (JPEG, PNG, etc.).
        current_user: Authenticated user extracted from the JWT.
        service: Injected ``DetectionService``.

    Returns:
        ``DetectionResponse`` with prediction details.

    Raises:
        HTTPException: 400 if the file is not a valid image.
        HTTPException: 401 if the user is not authenticated.
    """
    raise NotImplementedError("Not yet implemented")


@router.get(
    "/history",
    response_model=list[DetectionResponse],
    summary="Detection history",
    description="Retrieve the current user's detection history.",
)
async def get_detection_history(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    current_user: TokenData = Depends(get_current_user),
    service: DetectionService = Depends(get_detection_service),
) -> list[DetectionResponse]:
    """List the authenticated user's past detections.

    Args:
        skip: Pagination offset.
        limit: Page size.
        current_user: Authenticated user extracted from the JWT.
        service: Injected ``DetectionService``.

    Returns:
        List of ``DetectionResponse`` objects in reverse-chronological order.

    Raises:
        HTTPException: 401 if the user is not authenticated.
    """
    raise NotImplementedError("Not yet implemented")


@router.get(
    "/{detection_id}",
    response_model=DetectionResponse,
    summary="Get detection",
    description="Retrieve a specific detection result by its ID.",
)
async def get_detection(
    detection_id: int,
    current_user: TokenData = Depends(get_current_user),
    service: DetectionService = Depends(get_detection_service),
) -> DetectionResponse:
    """Retrieve a single detection result.

    Args:
        detection_id: Detection record primary key.
        current_user: Authenticated user extracted from the JWT.
        service: Injected ``DetectionService``.

    Returns:
        ``DetectionResponse`` if found.

    Raises:
        HTTPException: 404 if the detection record does not exist.
        HTTPException: 403 if the detection belongs to another user.
    """
    raise NotImplementedError("Not yet implemented")
