"""
test_detection.py — Real tests for the Plant Detection Pipeline
============================================================
Covers real model inference using predict.py and backend integration 
via DetectionService.
"""

import os
import sys
import pytest
import tempfile
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from PIL import Image

# Ensure project root and backend are in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from ml.predict import predict, map_class_name
from services.detection_service import DetectionService
from models.detection import DetectionResult
from models.plant import Plant
from schemas.detection import DetectionResponse

@pytest.fixture
def dummy_image():
    """Create a temporary 224x224 RGB image for testing."""
    temp_dir = tempfile.gettempdir()
    image_path = os.path.join(temp_dir, "test_leaf_dummy.jpg")
    img = Image.new("RGB", (224, 224), color=(73, 109, 137))
    img.save(image_path)
    yield image_path
    if os.path.exists(image_path):
        os.remove(image_path)

def test_map_class_name():
    """Verify raw folder names are correctly mapped to DB names."""
    assert map_class_name("Aloevera") == "Aloe Vera"
    assert map_class_name("amruthaballi") == "Giloy"
    assert map_class_name("bhrami") == "Brahmi"
    assert map_class_name("bringaraja") == "Bhringraj"
    assert map_class_name("amla") == "Amla"
    assert map_class_name("Curry") == "Curry Leaves"
    assert map_class_name("Drumstick") == "Moringa"
    assert map_class_name("Astma_weed") == "Astma Weed"

def test_real_inference_prediction(dummy_image):
    """Verify that PyTorch MobileNetV3 model loads and classifies the dummy image."""
    # Ensure model weights exist before running
    from ml.predict import MODEL_PATH as model_path
    if not os.path.exists(model_path):
        pytest.skip("Model weights not found. Skipping real inference test.")

    result = predict(dummy_image, top_k=5)
    
    assert "plant_name" in result
    assert "confidence" in result
    assert "top_predictions" in result
    assert "model_version" in result
    
    assert len(result["top_predictions"]) > 0
    assert isinstance(result["confidence"], float)
    assert 0.0 <= result["confidence"] <= 1.0
    
    # Every prediction must be one of the model's known classes (after name mapping)
    import json
    from ml.predict import MAPPING_PATH
    with open(MAPPING_PATH, encoding="utf-8") as f:
        known = {map_class_name(c) for c in json.load(f)}
    pred_names = [p["name"] for p in result["top_predictions"]]
    assert set(pred_names) <= known
    confidences = [p["confidence"] for p in result["top_predictions"]]
    assert confidences == sorted(confidences, reverse=True)

@pytest.mark.asyncio
async def test_detection_service_with_monograph(dummy_image):
    """Verify detect_plant resolves ID and persists record when plant exists in DB."""
    # Mock Repository and Session
    mock_session = AsyncMock()
    mock_repo = MagicMock()
    mock_repo.session = mock_session
    
    # Mock database query result finding Aloe Vera (ID=4)
    mock_plant = Plant(id=4, common_name="Aloe Vera", scientific_name="Aloe barbadensis Miller")
    mock_db_result = MagicMock()
    mock_db_result.scalars.return_value.all.return_value = [mock_plant]
    mock_session.execute.return_value = mock_db_result
    
    # Mock create result
    created_detection = DetectionResult(
        id=101,
        user_id=1,
        plant_id=4,
        image_path=dummy_image,
        confidence=0.92,
        model_version="mobilenetv3-v1.0.0",
        top_predictions=[{"name": "Aloe Vera", "confidence": 0.92, "plant_id": 4}],
        created_at=datetime.now(timezone.utc),
    )
    created_detection.plant = mock_plant
    mock_repo.create = AsyncMock(return_value=created_detection)
    mock_repo.get_with_plant = AsyncMock(return_value=created_detection)
    
    service = DetectionService(repository=mock_repo)
    
    # Read dummy image bytes
    with open(dummy_image, "rb") as f:
        image_bytes = f.read()
        
    result = await service.detect_plant(
        image_bytes=image_bytes,
        filename="aloe_test.jpg",
        user_id=1
    )
    
    assert result.id == 101
    assert result.plant_id == 4
    assert result.confidence == 0.92
    assert result.plant.common_name == "Aloe Vera"
    
    # Check response schema building
    response = service.build_response(result)
    assert isinstance(response, DetectionResponse)
    assert response.plant_id == 4
    assert response.plant_name == "Aloe Vera"
    assert response.scientific_name == "Aloe barbadensis Miller"

@pytest.mark.asyncio
async def test_detection_service_no_monograph(dummy_image):
    """Verify detect_plant sets plant_id=None and appends suffix if plant not in DB."""
    # Mock Repository and Session
    mock_session = AsyncMock()
    mock_repo = MagicMock()
    mock_repo.session = mock_session
    
    # Mock database query result returning empty list (no match in DB for Castor)
    mock_db_result = MagicMock()
    mock_db_result.scalars.return_value.all.return_value = []
    mock_session.execute.return_value = mock_db_result
    
    # Mock create result with plant_id=None
    created_detection = DetectionResult(
        id=102,
        user_id=1,
        plant_id=None,
        image_path=dummy_image,
        confidence=0.88,
        model_version="mobilenetv3-v1.0.0",
        top_predictions=[{"name": "Castor", "confidence": 0.88, "plant_id": None}],
        created_at=datetime.now(timezone.utc),
    )
    created_detection.plant = None
    mock_repo.create = AsyncMock(return_value=created_detection)
    mock_repo.get_with_plant = AsyncMock(return_value=created_detection)
    
    service = DetectionService(repository=mock_repo)
    
    with open(dummy_image, "rb") as f:
        image_bytes = f.read()
        
    result = await service.detect_plant(
        image_bytes=image_bytes,
        filename="castor_test.jpg",
        user_id=1
    )
    
    assert result.id == 102
    assert result.plant_id is None
    assert result.confidence == 0.88
    assert result.plant is None
    
    # Check response schema building handles out-of-scope classes correctly
    response = service.build_response(result)
    assert isinstance(response, DetectionResponse)
    assert response.plant_id is None
    assert response.plant_name == "Castor (No Monograph Available)"
    assert response.scientific_name == "N/A"


# ══════════════════════════════════════════════════════════════════
# Focused Endpoint Upload Enforcement Tests
# ══════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_detection_service():
    """Mock DetectionService to verify endpoint validation without ML/DB overhead."""
    from main import app
    from api.deps import get_detection_service

    mock = MagicMock()
    fake_detection = MagicMock()
    mock.detect_plant = AsyncMock(return_value=fake_detection)
    fake_response = DetectionResponse(
        id=999,
        plant_id=1,
        plant_name="Test Tulsi",
        scientific_name="Ocimum tenuiflorum",
        confidence=0.95,
        top_predictions=[],
        image_path="uploads/test.jpg",
        model_version="mobilenetv3-test",
        created_at=datetime.now(timezone.utc),
    )
    mock.build_response = MagicMock(return_value=fake_response)

    app.dependency_overrides[get_detection_service] = lambda: mock
    yield mock
    app.dependency_overrides.pop(get_detection_service, None)


class TestDetectionUploadLimits:
    """Validate bounded read, size enforcement, empty-file, and MIME type checks."""

    def test_upload_exact_limit_accepted(self, client, mock_detection_service, monkeypatch):
        """Upload exactly at the configured size limit is accepted by size validation."""
        from config.settings import settings
        monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

        limit_bytes = 1 * 1024 * 1024
        payload = b"X" * limit_bytes
        response = client.post(
            "/api/v1/detect/",
            files={"image": ("exact_limit.jpg", payload, "image/jpeg")},
        )

        assert response.status_code == 201
        assert response.json()["plant_name"] == "Test Tulsi"
        mock_detection_service.detect_plant.assert_called_once()

    def test_upload_one_byte_over_limit_rejected(self, client, mock_detection_service, monkeypatch):
        """Upload 1 byte over the limit is rejected with HTTP 413 before detection."""
        from config.settings import settings
        monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

        oversized_bytes = (1 * 1024 * 1024) + 1
        payload = b"X" * oversized_bytes
        response = client.post(
            "/api/v1/detect/",
            files={"image": ("one_byte_over.jpg", payload, "image/jpeg")},
        )

        assert response.status_code == 413
        body = response.json()
        assert body["success"] is False
        assert "exceeds maximum allowed size" in body["message"]
        assert body["detail"]["code"] == "PAYLOAD_TOO_LARGE"
        mock_detection_service.detect_plant.assert_not_called()

    def test_empty_upload_rejected(self, client, mock_detection_service):
        """Empty upload (0 bytes) is rejected with HTTP 400."""
        response = client.post(
            "/api/v1/detect/",
            files={"image": ("empty.jpg", b"", "image/jpeg")},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert "empty" in body["message"].lower()
        mock_detection_service.detect_plant.assert_not_called()

    def test_disallowed_mime_type_rejected(self, client, mock_detection_service):
        """Upload with disallowed MIME type is rejected with HTTP 400."""
        response = client.post(
            "/api/v1/detect/",
            files={"image": ("document.pdf", b"fake pdf content", "application/pdf")},
        )

        assert response.status_code == 400
        body = response.json()
        assert body["success"] is False
        assert "invalid image type" in body["message"].lower()
        mock_detection_service.detect_plant.assert_not_called()

    def test_oversized_upload_never_invokes_service(self, client, mock_detection_service, monkeypatch):
        """Oversized upload halts processing immediately without invoking detection service."""
        from config.settings import settings
        monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_MB", 1)

        payload = b"X" * (1 * 1024 * 1024 + 4096)
        response = client.post(
            "/api/v1/detect/",
            files={"image": ("too_large.png", payload, "image/png")},
        )

        assert response.status_code == 413
        mock_detection_service.detect_plant.assert_not_called()
        mock_detection_service.build_response.assert_not_called()

    def test_upload_read_failure_closes_file_and_skips_service(self, client, mock_detection_service, monkeypatch):
        """Verify upload file is closed if reading it raises an I/O exception."""
        from starlette.datastructures import UploadFile

        close_called = False
        orig_close = UploadFile.close

        async def spy_close(self):
            nonlocal close_called
            close_called = True
            return await orig_close(self)

        monkeypatch.setattr(UploadFile, "close", spy_close)
        monkeypatch.setattr(
            UploadFile,
            "read",
            AsyncMock(side_effect=OSError("Disk read failure")),
        )

        with pytest.raises(OSError, match="Disk read failure"):
            client.post(
                "/api/v1/detect/",
                files={"image": ("corrupt.jpg", b"valid_start", "image/jpeg")},
            )

        assert close_called is True
        mock_detection_service.detect_plant.assert_not_called()
