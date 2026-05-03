from pydantic import BaseModel, Field
from typing import Optional, Literal


class TextRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Natural language appointment request")


class ImageRequest(BaseModel):
    file: bytes = Field(..., description="Image file for OCR")


class OCRResult(BaseModel):
    raw_text: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class Entities(BaseModel):
    date_phrase: Optional[str] = None
    time_phrase: Optional[str] = None
    department: Optional[str] = None


class EntityExtractionResult(BaseModel):
    entities: Entities
    entities_confidence: float = Field(..., ge=0.0, le=1.0)


class NormalizedData(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    tz: str = "Asia/Kolkata"


class NormalizationResult(BaseModel):
    normalized: NormalizedData
    normalization_confidence: float = Field(..., ge=0.0, le=1.0)


class GuardrailResult(BaseModel):
    status: Literal["ok", "needs_clarification"]
    message: Optional[str] = None


class AppointmentData(BaseModel):
    department: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    tz: str = "Asia/Kolkata"


class AppointmentResult(BaseModel):
    appointment: AppointmentData
    status: Literal["ok", "needs_clarification"]
    message: Optional[str] = None


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None