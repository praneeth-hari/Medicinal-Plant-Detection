"""
Detection Service
=================

Business-logic layer for plant image detection.  Coordinates image
saving, mock ML inference (real model to be integrated in Phase 4),
and persistence of detection results via ``DetectionRepository``.
"""
from __future__ import annotations

import asyncio
import hashlib
import logging
import os
import uuid
from datetime import datetime, timezone
from typing import Sequence

import aiofiles

from api.exceptions import ForbiddenException, NotFoundException
from config.settings import settings
from models.detection import DetectionResult
from repositories.detection_repository import DetectionRepository
from schemas.detection import DetectionResponse, PredictionItem

logger = logging.getLogger(__name__)

# Mock predictions used until the real ML model is integrated (Phase 4).
_MOCK_PREDICTIONS: list[dict] = [
    {"plant_id": 1, "name": "Tulsi", "confidence": 0.85},
    {"plant_id": 2, "name": "Neem", "confidence": 0.10},
    {"plant_id": 3, "name": "Ashwagandha", "confidence": 0.05},
]


class DetectionService:
    """Service handling plant detection from uploaded images.

    Uses mock predictions until the real ML model is integrated.

    Args:
        repository: Injected ``DetectionRepository`` instance.
    """

    def __init__(self, repository: DetectionRepository) -> None:
        """Initialise the service with a detection repository.

        Args:
            repository: Data-access dependency.
        """
        self.repository = repository

    async def detect_plant(
        self,
        image_bytes: bytes,
        filename: str,
        user_id: int,
        *,
        model_version: str | None = None,
    ) -> DetectionResult:
        """Run plant detection on an uploaded image (real inference).

        Steps:
        1. Save the uploaded image to ``UPLOAD_DIR``.
        2. Perform inference using the trained PyTorch MobileNetV3 model.
        3. Persist the result via the repository.
        4. Return the ORM model with plant relationship loaded.

        Args:
            image_bytes: Raw bytes of the uploaded image file.
            filename: Original filename for extension extraction.
            user_id: ID of the authenticated user submitting the image.
            model_version: Optional model checkpoint identifier.

        Returns:
            ``DetectionResult`` ORM model with plant data.
        """
        # 1. Save the uploaded image
        image_path = await self._save_image(image_bytes, filename)

        # 2. Perform real model inference (or fall back to mock predictions)
        try:
            from ml.predict import predict  # noqa: PLC0415
            from models.plant import Plant  # noqa: PLC0415
            from sqlalchemy import select, func  # noqa: PLC0415

            abs_image_path = os.path.abspath(image_path)
            inference_result = predict(abs_image_path)
            top_predictions = inference_result["top_predictions"]
            version = model_version or inference_result.get("model_version", "mobilenetv3-v1.0.0")

            # Query SQLite to resolve plant IDs dynamically
            names_to_query = [p["name"] for p in top_predictions]
            stmt = select(Plant).where(func.lower(Plant.common_name).in_([n.lower() for n in names_to_query]))
            db_plants_res = await self.repository.session.execute(stmt)
            db_plants = db_plants_res.scalars().all()

            plant_id_lookup = {p.common_name.lower(): p.id for p in db_plants}
            for pred in top_predictions:
                pred["plant_id"] = plant_id_lookup.get(pred["name"].lower())
            top_plant_id = plant_id_lookup.get(top_predictions[0]["name"].lower())

        except Exception as exc:
            logger.warning(
                "ML inference unavailable (%s). Using mock predictions.", exc,
            )
            top_predictions = list(_MOCK_PREDICTIONS)  # shallow copy
            top_plant_id = top_predictions[0].get("plant_id")
            version = model_version or "mock-v0.0.0"

        top_prediction = top_predictions[0]
        # 3. Persist detection result
        detection_data = {
            "user_id": user_id,
            "plant_id": top_plant_id,
            "image_path": image_path,
            "confidence": top_prediction["confidence"],
            "model_version": version,
            "top_predictions": top_predictions,
        }
        detection = await self.repository.create(detection_data)

        logger.info(
            "Detection created: id=%d user=%d plant_id=%s confidence=%.2f",
            detection.id, user_id, detection.plant_id, detection.confidence,
        )

        # 4. Return with plant relationship loaded
        result = await self.repository.get_with_plant(detection.id)
        return result  # type: ignore[return-value]

    async def get_detection(
        self, detection_id: int, user_id: int,
    ) -> DetectionResult:
        """Retrieve a single detection result.

        Verifies that the detection belongs to the requesting user.

        Args:
            detection_id: Detection record primary key.
            user_id: Authenticated user's ID.

        Returns:
            ``DetectionResult`` ORM model.

        Raises:
            NotFoundException: If the detection record does not exist.
            ForbiddenException: If the detection belongs to another user.
        """
        detection = await self.repository.get_with_plant(detection_id)
        if detection is None:
            raise NotFoundException("Detection", detection_id)
        if detection.user_id != user_id:
            raise ForbiddenException("You do not own this detection result")
        return detection

    async def get_history(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[DetectionResult]:
        """Retrieve the detection history for a user.

        Args:
            user_id: User's primary key.
            skip: Pagination offset.
            limit: Max results.

        Returns:
            Sequence of ``DetectionResult`` ORM models with plant data.
        """
        return await self.repository.get_by_user(
            user_id, skip=skip, limit=limit,
        )

    def build_response(self, detection: DetectionResult) -> DetectionResponse:
        """Convert a DetectionResult ORM model to a response schema.

        Populates ``plant_name`` and ``scientific_name`` from the
        eagerly-loaded plant relationship.

        Args:
            detection: ORM model with plant relationship loaded.

        Returns:
            ``DetectionResponse`` Pydantic schema.
        """
        plant_name = None
        scientific_name = None
        if detection.plant is not None:
            plant_name = detection.plant.common_name
            scientific_name = detection.plant.scientific_name
        elif detection.top_predictions:
            # Append (No Monograph Available) to the predicted plant name when not in the DB
            raw_pred_name = detection.top_predictions[0]["name"]
            plant_name = f"{raw_pred_name} (No Monograph Available)"
            scientific_name = "N/A"

        top_preds = None
        if detection.top_predictions:
            top_preds = [
                PredictionItem(**p) for p in detection.top_predictions
            ]

        return DetectionResponse(
            id=detection.id,
            plant_id=detection.plant_id,
            plant_name=plant_name,
            scientific_name=scientific_name,
            confidence=detection.confidence,
            top_predictions=top_preds,
            image_path=detection.image_path,
            model_version=detection.model_version,
            created_at=detection.created_at,
        )

    @staticmethod
    async def _save_image(image_bytes: bytes, filename: str) -> str:
        """Save uploaded image bytes to the upload directory using async I/O.

        Generates a unique filename to prevent collisions.

        Args:
            image_bytes: Raw file bytes.
            filename: Original filename (used for extension).

        Returns:
            Path to the saved image.
        """
        upload_dir = settings.upload_path
        os.makedirs(upload_dir, exist_ok=True)

        ext = os.path.splitext(filename)[1] if filename else ".jpg"
        unique_name = f"{uuid.uuid4().hex}{ext}"
        file_path = str(os.path.join(upload_dir, unique_name))

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(image_bytes)

        logger.debug("Saved image: %s (%d bytes)", file_path, len(image_bytes))
        return file_path
