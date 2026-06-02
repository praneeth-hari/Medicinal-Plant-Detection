"""
Schemas (Pydantic models) package.

Exports request / response schemas for all domain entities.
"""
from schemas.common import (
    MessageResponse,
    PaginatedResponse,
    ErrorResponse,
    HealthResponse,
)
from schemas.plant import (
    PlantBase,
    PlantCreate,
    PlantUpdate,
    PlantResponse,
    PlantListResponse,
)
from schemas.user import (
    UserBase,
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    TokenData,
)
from schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ChatSessionResponse,
    ChatSessionDetailResponse,
    SourceReference,
)
from schemas.detection import (
    DetectionResponse,
    DetectionHistoryResponse,
    PredictionItem,
)

__all__ = [
    "MessageResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "HealthResponse",
    "PlantBase",
    "PlantCreate",
    "PlantUpdate",
    "PlantResponse",
    "PlantListResponse",
    "UserBase",
    "UserCreate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenData",
    "ChatRequest",
    "ChatResponse",
    "ChatMessageResponse",
    "ChatSessionResponse",
    "ChatSessionDetailResponse",
    "SourceReference",
    "DetectionResponse",
    "DetectionHistoryResponse",
    "PredictionItem",
]
