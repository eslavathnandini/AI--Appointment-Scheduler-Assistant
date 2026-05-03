import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import pytz
from dateutil import parser as date_parser
from app.config import settings


class NormalizationService:
    def __init__(self):
        self.tz = pytz.timezone(settings.timezone)
    
    def normalize(self, date_phrase: Optional[str], time_phrase: Optional[str]) -> dict:
        """Normalize date and time phrases to ISO format in Asia/Kolkata timezone"""
        
        normalized_date = self._normalize_date(date_phrase)
        normalized_time = self._normalize_time(time_phrase)
        
        confidence = self._calculate_normalization_confidence(
            normalized_date, normalized_time
        )
        
        return {
            "normalized": {
                "date": normalized_date,
                "time": normalized_time,
                "tz": settings.timezone
            },
            "normalization_confidence": confidence
        }
    
    def _normalize_date(self, date_phrase: Optional[str]) -> Optional[str]:
        """Convert date phrase to ISO format YYYY-MM-DD"""
        if not date_phrase:
            return None
        
        date_phrase_lower = date_phrase.lower().strip()
        now = datetime.now(self.tz)
        
        try:
            if "tomorrow" in date_phrase_lower:
                target_date = now + timedelta(days=1)
                return target_date.strftime("%Y-%m-%d")
            
            if "today" in date_phrase_lower:
                return now.strftime("%Y-%m-%d")
            
            day_names = {
                "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                "friday": 4, "saturday": 5, "sunday": 6
            }
            
            for day_name, day_num in day_names.items():
                if day_name in date_phrase_lower:
                    current_day = now.weekday()
                    
                    if "next" in date_phrase_lower:
                        days_ahead = (day_num - current_day + 7) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                    else:
                        days_ahead = (day_num - current_day + 7) % 7
                        if days_ahead == 0:
                            days_ahead = 7
                    
                    target_date = now + timedelta(days=days_ahead)
                    return target_date.strftime("%Y-%m-%d")
            
            match = re.search(r"(\d{1,2})(?:st|nd|rd|th)?\s+(\w+)", date_phrase_lower)
            if match:
                day_num = int(match.group(1))
                month_name = match.group(2)
                month_num = self._month_to_number(month_name)
                if month_num:
                    try:
                        target_date = datetime(now.year, month_num, day_num, tzinfo=self.tz)
                        if target_date < now:
                            target_date = target_date.replace(year=now.year + 1)
                        return target_date.strftime("%Y-%m-%d")
                    except ValueError:
                        pass
            
            match = re.search(r"(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?", date_phrase_lower)
            if match:
                month = int(match.group(1))
                day = int(match.group(2))
                year = int(match.group(3)) if match.group(3) else now.year
                if year < 100:
                    year += 2000
                try:
                    target_date = datetime(year, month, day, tzinfo=self.tz)
                    return target_date.strftime("%Y-%m-%d")
                except ValueError:
                    pass
            
            try:
                parsed = date_parser.parse(date_phrase)
                if parsed:
                    localized = self.tz.localize(parsed)
                    return localized.strftime("%Y-%m-%d")
            except:
                pass
            
        except Exception as e:
            pass
        
        return None
    
    def _normalize_time(self, time_phrase: Optional[str]) -> Optional[str]:
        """Convert time phrase to HH:MM format (24-hour)"""
        if not time_phrase:
            return None
        
        time_phrase_lower = time_phrase.lower().strip()
        
        try:
            if "morning" in time_phrase_lower:
                if "12" in time_phrase_lower or "noon" in time_phrase_lower:
                    return "12:00"
                return "09:00"
            
            if "afternoon" in time_phrase_lower:
                return "14:00"
            
            if "evening" in time_phrase_lower:
                return "18:00"
            
            if "noon" in time_phrase_lower:
                return "12:00"
            
            if "midnight" in time_phrase_lower:
                return "00:00"
            
            match = re.search(r"(\d{1,2}):(\d{2})\s*(am|pm)?", time_phrase_lower)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                period = match.group(3)
                
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                return f"{hour:02d}:{minute:02d}"
            
            match = re.search(r"(\d{1,2})\s*(am|pm)", time_phrase_lower)
            if match:
                hour = int(match.group(1))
                period = match.group(2)
                
                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0
                
                return f"{hour:02d}:00"
            
        except Exception:
            pass
        
        return None
    
    def _month_to_number(self, month_name: str) -> Optional[int]:
        """Convert month name to number"""
        months = {
            "january": 1, "jan": 1,
            "february": 2, "feb": 2,
            "march": 3, "mar": 3,
            "april": 4, "apr": 4,
            "may": 5,
            "june": 6, "jun": 6,
            "july": 7, "jul": 7,
            "august": 8, "aug": 8,
            "september": 9, "sep": 9, "sept": 9,
            "october": 10, "oct": 10,
            "november": 11, "nov": 11,
            "december": 12, "dec": 12
        }
        return months.get(month_name.lower())
    
    def _calculate_normalization_confidence(
        self, 
        normalized_date: Optional[str], 
        normalized_time: Optional[str]
    ) -> float:
        """Calculate confidence of normalization"""
        score = 0.0
        count = 0
        
        if normalized_date:
            score += 0.95
        count += 1
        
        if normalized_time:
            score += 0.85
        count += 1
        
        if count == 0:
            return 0.0
        
        return round(score / count, 2)


normalization_service = NormalizationService()