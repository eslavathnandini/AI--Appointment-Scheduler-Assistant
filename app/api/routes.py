from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
import json

from app.api.models import (
    TextRequest,
    OCRResult,
    EntityExtractionResult,
    NormalizationResult,
    GuardrailResult,
    AppointmentResult,
    ErrorResponse
)
from app.services.ocr_service import ocr_service
from app.services.extraction_service import extraction_service
from app.services.normalize_service import normalization_service
from app.services.guardrail_service import guardrail_service


router = APIRouter(prefix="/api/v1", tags=["extraction"])


@router.post("/extract/text", response_model=AppointmentResult)
async def extract_from_text(request: TextRequest):
    """
    Process text input and extract appointment details.
    """
    try:
        raw_text = request.text
        ocr_result = {"raw_text": raw_text, "confidence": 0.95}
        
        entity_result = extraction_service.extract_entities(raw_text)
        
        date_phrase = entity_result["entities"]["date_phrase"]
        time_phrase = entity_result["entities"]["time_phrase"]
        
        normalization_result = normalization_service.normalize(date_phrase, time_phrase)
        
        guardrail_result = guardrail_service.validate(
            department=entity_result["entities"]["department"],
            date=normalization_result["normalized"]["date"],
            time=normalization_result["normalized"]["time"]
        )
        
        if guardrail_result["status"] == "needs_clarification":
            return AppointmentResult(
                appointment={
                    "department": entity_result["entities"]["department"],
                    "date": normalization_result["normalized"]["date"],
                    "time": normalization_result["normalized"]["time"],
                    "tz": normalization_result["normalized"]["tz"]
                },
                status="needs_clarification",
                message=guardrail_result["message"]
            )
        
        return AppointmentResult(
            appointment={
                "department": entity_result["entities"]["department"],
                "date": normalization_result["normalized"]["date"],
                "time": normalization_result["normalized"]["time"],
                "tz": normalization_result["normalized"]["tz"]
            },
            status="ok"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract/image", response_model=AppointmentResult)
async def extract_from_image(
    file: UploadFile = File(...)
):
    """
    Process image input with OCR and extract appointment details.
    """
    try:
        allowed_types = {"image/png", "image/jpeg", "image/jpg", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Supported: PNG, JPEG, JPG, WEBP"
            )
        
        contents = await file.read()
        
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail="File too large. Maximum size: 10MB"
            )
        
        raw_text, ocr_confidence = ocr_service.extract_from_file(
            contents, 
            file.filename or "image.png"
        )
        
        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the image"
            )
        
        guardrail_check = guardrail_service.validate_raw_text(raw_text)
        
        entity_result = extraction_service.extract_entities(raw_text)
        
        date_phrase = entity_result["entities"]["date_phrase"]
        time_phrase = entity_result["entities"]["time_phrase"]
        
        normalization_result = normalization_service.normalize(date_phrase, time_phrase)
        
        guardrail_result = guardrail_service.validate(
            department=entity_result["entities"]["department"],
            date=normalization_result["normalized"]["date"],
            time=normalization_result["normalized"]["time"]
        )
        
        if guardrail_result["status"] == "needs_clarification":
            return AppointmentResult(
                appointment={
                    "department": entity_result["entities"]["department"],
                    "date": normalization_result["normalized"]["date"],
                    "time": normalization_result["normalized"]["time"],
                    "tz": normalization_result["normalized"]["tz"]
                },
                status="needs_clarification",
                message=guardrail_result["message"]
            )
        
        return AppointmentResult(
            appointment={
                "department": entity_result["entities"]["department"],
                "date": normalization_result["normalized"]["date"],
                "time": normalization_result["normalized"]["time"],
                "tz": normalization_result["normalized"]["tz"]
            },
            status="ok"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "appointment-scheduler"}