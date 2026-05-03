import re
from typing import Optional
from app.config import settings


class ExtractionService:
    def __init__(self):
        pass
    
    def extract_entities(self, text: str) -> dict:
        """Extract date, time, and department entities from text"""
        
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
            "dentist": ["dentist", "dental", "tooth", "teeth"],
            "doctor": ["doctor", "dr", "physician", "medical"],
            "cardiologist": ["cardio", "heart"],
            "dermatologist": ["derma", "skin"],
            "neurologist": ["neuro", "brain", "nerve"],
            "orthopedist": ["ortho", "bone", "joint"],
            "ophthalmologist": ["eye", "ophthal"],
            "pediatrician": ["pediatric", "child", "kids"],
            "psychiatrist": ["psych", "mental", "therapy"],
            "gynecologist": ["gyn", "women", "pregnancy"],
            "urologist": ["uro", "urinary"],
            "ent": ["ent", "ear", "nose", "throat"],
            "physiotherapist": ["physio", "physical therapy"],
            "veterinarian": ["vet", "pet", "animal"]
        }
        
        for dept, keywords in department_patterns.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return dept.capitalize()
        
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