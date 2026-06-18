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

import logging

from fastapi import APIRouter, Depends, Query, UploadFile, File, status

from api.deps import get_current_user, get_detection_service
from api.exceptions import BadRequestException
from schemas.detection import DetectionResponse
from schemas.user import TokenData
from services.detection_service import DetectionService

logger = logging.getLogger(__name__)

router = APIRouter()

# Allowed image MIME types
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp", "image/tiff"}


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

    Reads the uploaded file bytes, validates it is an image,
    delegates to ``DetectionService`` for inference, and returns
    the prediction result.

    Args:
        image: Uploaded image file (JPEG, PNG, WebP, etc.).
        current_user: Authenticated user extracted from the JWT.
        service: Injected ``DetectionService``.

    Returns:
        ``DetectionResponse`` with prediction details.

    Raises:
        BadRequestException: If the file is not a valid image type.
    """
    # Validate file type
    content_type = image.content_type or ""
    if content_type not in _ALLOWED_TYPES:
        raise BadRequestException(
            f"Invalid image type '{content_type}'. "
            f"Allowed: {', '.join(sorted(_ALLOWED_TYPES))}"
        )

    # Read image bytes
    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise BadRequestException("Uploaded file is empty")

    # Run detection
    detection = await service.detect_plant(
        image_bytes=image_bytes,
        filename=image.filename or "upload.jpg",
        user_id=current_user.user_id,
    )
    return service.build_response(detection)


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
    """
    detections = await service.get_history(
        current_user.user_id, skip=skip, limit=limit,
    )
    return [service.build_response(d) for d in detections]


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
        ``DetectionResponse`` if found and owned by the user.

    Raises:
        NotFoundException: 404 if the detection record does not exist.
        ForbiddenException: 403 if the detection belongs to another user.
    """
    detection = await service.get_detection(
        detection_id, current_user.user_id,
    )
    return service.build_response(detection)
