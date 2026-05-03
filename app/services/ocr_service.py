import requests
import json
from app.config import settings
from typing import Tuple, Optional


class OCRService:
    def __init__(self):
        self.api_key = settings.ocr_api_key
        self.api_url = "https://api.ocr.space/parse/image"
    
    def extract_from_url(self, url: str) -> Tuple[str, float]:
        """Extract text from image URL"""
        payload = {
            "url": url,
            "isOverlayRequired": False,
            "apikey": self.api_key,
            "language": "eng",
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2
        }
        
        try:
            response = requests.post(self.api_url, data=payload, timeout=30)
            result = response.json()
            
            if result.get("IsErroredOnProcessing"):
                raise Exception(result.get("ErrorMessage", "OCR processing failed"))
            
            parsed_results = result.get("ParsedResults", [])
            if not parsed_results:
                raise Exception("No text found in image")
            
            first_result = parsed_results[0]
            text = first_result.get("ParsedText", "").strip()
            
            text_overlay = first_result.get("TextOverlay", {})
            lines = text_overlay.get("Lines", [])
            confidence_score = self._calculate_confidence(lines)
            
            return text, confidence_score
            
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def extract_from_file(self, file_bytes: bytes, filename: str) -> Tuple[str, float]:
        """Extract text from image file bytes"""
        files = {"file": (filename, file_bytes, "image/png")}
        payload = {
            "isOverlayRequired": False,
            "apikey": self.api_key,
            "language": "eng",
            "detectOrientation": True,
            "scale": True,
            "OCREngine": 2
        }
        
        try:
            response = requests.post(self.api_url, files=files, data=payload, timeout=30)
            result = response.json()
            
            if result.get("IsErroredOnProcessing"):
                raise Exception(result.get("ErrorMessage", "OCR processing failed"))
            
            parsed_results = result.get("ParsedResults", [])
            if not parsed_results:
                raise Exception("No text found in image")
            
            first_result = parsed_results[0]
            text = first_result.get("ParsedText", "").strip()
            
            text_overlay = first_result.get("TextOverlay", {})
            lines = text_overlay.get("Lines", [])
            confidence_score = self._calculate_confidence(lines)
            
            return text, confidence_score
            
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def _calculate_confidence(self, lines: list) -> float:
        """Calculate confidence score based on OCR confidence values"""
        if not lines:
            return 0.5
        
        total_confidence = 0.0
        count = 0
        
        for line in lines:
            words = line.get("Words", [])
            for word in words:
                conf = word.get("Confidence", 0)
                if conf > 0:
                    total_confidence += conf / 100.0
                    count += 1
        
        if count == 0:
            return 0.5
        
        return round(total_confidence / count, 2)


ocr_service = OCRService()