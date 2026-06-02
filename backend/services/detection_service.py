"""
Detection Service
=================

Business-logic layer for plant image detection.  Coordinates between
the ML model inference pipeline and the ``DetectionRepository`` for
persisting results.
"""

from __future__ import annotations

from typing import Sequence

from repositories.detection_repository import DetectionRepository
from schemas.detection import DetectionResponse


class DetectionService:
    """Service handling plant detection from uploaded images.

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
        user_id: int,
        *,
        model_version: str | None = None,
    ) -> DetectionResponse:
        """Run the plant classification model on an uploaded image.

        Steps (to be implemented):
        1. Save the uploaded image to ``UPLOAD_DIR``.
        2. Preprocess the image for model input.
        3. Run inference and obtain top-K predictions.
        4. Persist the result via the repository.
        5. Return the ``DetectionResponse``.

        Args:
            image_bytes: Raw bytes of the uploaded image file.
            user_id: ID of the authenticated user submitting the image.
            model_version: Optional model checkpoint to use.

        Returns:
            ``DetectionResponse`` with prediction details.
        """
        raise NotImplementedError("Not yet implemented")

    async def get_history(
        self,
        user_id: int,
        *,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[DetectionResponse]:
        """Retrieve the detection history for a user.

        Args:
            user_id: User's primary key.
            skip: Pagination offset.
            limit: Max results.

        Returns:
            Sequence of ``DetectionResponse`` objects.
        """
        raise NotImplementedError("Not yet implemented")
