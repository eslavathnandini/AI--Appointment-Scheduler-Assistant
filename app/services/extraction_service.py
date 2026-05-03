import re
import requests
import json
from typing import Optional
from app.config import settings


class ExtractionService:
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.gemini_endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent"
    
    def extract_entities(self, text: str) -> dict:
        """Extract date, time, and department entities using Gemini API via REST"""
        
        if self.gemini_api_key:
            return self._extract_with_gemini(text)
        else:
            return self._extract_with_rules(text)
    
    def _extract_with_gemini(self, text: str) -> dict:
        """Extract entities using Gemini API via REST with confidence scores"""
        
        prompt = f"""Extract appointment entities from the following text and return a JSON object with confidence scores.

Text: "{text}"

Return a JSON object with this exact format:
{{
  "entities": {{
    "date_phrase": "extracted date phrase or null",
    "time_phrase": "extracted time phrase or null",
    "department": "extracted department/doctor type or null"
  }},
  "entities_confidence": confidence_score_between_0_and_1
}}

Supported departments: Dentist, Doctor, Cardiologist, Dermatologist, Neurologist, Orthopedist, Ophthalmologist, Pediatrician, Psychiatrist, Gynecologist, Urologist, ENT, Physiotherapist, Veterinarian

Date formats to recognize: "next Friday", "tomorrow", "today", "25th December", "12/25/2025", day names (Monday-Sunday)

Time formats to recognize: "3pm", "3:30pm", "10am", "morning", "afternoon", "evening", "noon"

Return ONLY valid JSON, no other text."""

        url = f"{self.gemini_endpoint}?key={self.gemini_api_key}"
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 1000
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    content = result['candidates'][0].get('content', {})
                    parts = content.get('parts', [])
                    
                    if parts:
                        response_text = parts[0].get('text', '')
                        
                        json_match = re.search(r'\{[\s\S]*\}', response_text)
                        if json_match:
                            extracted = json.loads(json_match.group(0))
                            
                            return {
                                "entities": {
                                    "date_phrase": extracted.get("entities", {}).get("date_phrase"),
                                    "time_phrase": extracted.get("entities", {}).get("time_phrase"),
                                    "department": extracted.get("entities", {}).get("department")
                                },
                                "entities_confidence": extracted.get("entities_confidence", 0.9)
                            }
            
            print(f"Gemini API error: {response.status_code} - {response.text}")
            
        except Exception as e:
            print(f"Gemini extraction failed: {e}")
        
        return self._extract_with_rules(text)
    
    def _extract_with_rules(self, text: str) -> dict:
        """Fallback rule-based extraction"""
        
        import re
        
        department = self._extract_department(text)
        date_phrase = self._extract_date_phrase(text)
        time_phrase = self._extract_time_phrase(text)
        
        confidence = self._calculate_extraction_confidence(
            department, date_phrase, time_phrase
        )
        
        return {
            "entities": {
                "date_phrase": date_phrase,
                "time_phrase": time_phrase,
                "department": department
            },
            "entities_confidence": confidence
        }
    
    def _extract_department(self, text: str) -> Optional[str]:
        """Extract department/doctor type from text"""
        text_lower = text.lower()
        
        department_patterns = {
            "Dentist": ["dentist", "dental", "tooth", "teeth"],
            "Doctor": ["doctor", "dr ", "physician", "medical"],
            "Cardiologist": ["cardio", "heart specialist"],
            "Dermatologist": ["derma", "skin"],
            "Neurologist": ["neuro", "brain", "nerve"],
            "Orthopedist": ["ortho", "bone", "joint"],
            "Ophthalmologist": ["eye", "ophthal"],
            "Pediatrician": ["pediatric", "child", "kids"],
            "Psychiatrist": ["psych", "mental", "therapy"],
            "Gynecologist": ["gyn", "women", "pregnancy"],
            "Urologist": ["uro", "urinary"],
            "ENT": ["ent", "ear", "nose", "throat"],
            "Physiotherapist": ["physio", "physical therapy"],
            "Veterinarian": ["vet", "pet", "animal"]
        }
        
        for dept, keywords in department_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return dept
        
        return None
    
    def _extract_date_phrase(self, text: str) -> Optional[str]:
        """Extract date-related phrase from text"""
        text_lower = text.lower()
        
        date_patterns = [
            r"next\s+\w+day",
            r"this\s+\w+day",
            r"\w+day",
            r"\d{1,2}(?:st|nd|rd|th)?\s+\w+",
            r"\d{1,2}/\d{1,2}(?:/\d{2,4})?",
            r"\d{4}-\d{2}-\d{2}",
            r"tomorrow",
            r"today",
            r"monday|tuesday|wednesday|thursday|friday|saturday|sunday"
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)
        
        return None
    
    def _extract_time_phrase(self, text: str) -> Optional[str]:
        """Extract time-related phrase from text"""
        text_lower = text.lower()
        
        time_patterns = [
            r"\d{1,2}:\d{2}\s*(?:am|pm)?",
            r"\d{1,2}\s*(?:am|pm)",
            r"morning",
            r"afternoon",
            r"evening",
            r"noon",
            r"midnight"
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, text_lower)
            if match:
                return match.group(0)
        
        return None
    
    def _calculate_extraction_confidence(
        self, 
        department: Optional[str], 
        date_phrase: Optional[str], 
        time_phrase: Optional[str]
    ) -> float:
        """Calculate confidence based on how many entities were extracted"""
        score = 0.0
        count = 0
        
        if department:
            score += 0.9
        count += 1
        
        if date_phrase:
            score += 0.85
        count += 1
        
        if time_phrase:
            score += 0.85
        count += 1
        
        if count == 0:
            return 0.0
        
        return round(score / count, 2)


extraction_service = ExtractionService()