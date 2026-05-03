import pytest
from app.services.extraction_service import extraction_service
from app.services.normalize_service import normalization_service
from app.services.guardrail_service import guardrail_service


class TestExtractionService:
    def test_extract_entities_basic(self):
        text = "Book dentist next Friday at 3pm"
        result = extraction_service.extract_entities(text)
        
        assert result["entities"]["department"] is not None
        assert result["entities"]["date_phrase"] is not None
        assert result["entities"]["time_phrase"] is not None
        assert result["entities_confidence"] > 0
    
    def test_extract_department(self):
        text = "Book dentist"
        result = extraction_service.extract_entities(text)
        assert result["entities"]["department"] == "Dentist"
    
    def test_extract_date_phrase(self):
        text = "next Friday"
        result = extraction_service.extract_entities(text)
        assert result["entities"]["date_phrase"] is not None
    
    def test_extract_time_phrase(self):
        text = "3pm"
        result = extraction_service.extract_entities(text)
        assert result["entities"]["time_phrase"] is not None


class TestNormalizationService:
    def test_normalize_date_next_friday(self):
        result = normalization_service.normalize("next Friday", "3pm")
        
        assert result["normalized"]["date"] is not None
        assert result["normalized"]["time"] is not None
        assert result["normalized"]["tz"] == "Asia/Kolkata"
    
    def test_normalize_time_3pm(self):
        result = normalization_service.normalize("next Friday", "3pm")
        assert result["normalized"]["time"] == "15:00"
    
    def test_normalize_tomorrow(self):
        result = normalization_service.normalize("tomorrow", "10am")
        assert result["normalized"]["date"] is not None
    
    def test_normalize_empty(self):
        result = normalization_service.normalize(None, None)
        assert result["normalized"]["date"] is None
        assert result["normalized"]["time"] is None


class TestGuardrailService:
    def test_validate_complete_data(self):
        result = guardrail_service.validate("dentist", "2025-09-26", "15:00")
        
        assert result["status"] == "ok"
    
    def test_validate_missing_department(self):
        result = guardrail_service.validate(None, "2025-09-26", "15:00")
        
        assert result["status"] == "needs_clarification"
    
    def test_validate_missing_date(self):
        result = guardrail_service.validate("dentist", None, "15:00")
        
        assert result["status"] == "needs_clarification"
    
    def test_validate_missing_time(self):
        result = guardrail_service.validate("dentist", "2025-09-26", None)
        
        assert result["status"] == "needs_clarification"
    
    def test_validate_raw_text_vague(self):
        result = guardrail_service.validate_raw_text("Book dentist sometime")
        
        assert result["status"] == "needs_clarification"
    
    def test_validate_raw_text_specific(self):
        result = guardrail_service.validate_raw_text("Book dentist next Friday at 3pm")
        
        assert result["status"] == "ok"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])