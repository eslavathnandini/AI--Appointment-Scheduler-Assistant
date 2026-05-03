from typing import Optional


class GuardrailService:
    def __init__(self):
        self.valid_departments = {
            "dentist", "doctor", "cardiologist", "dermatologist", "neurologist",
            "orthopedist", "ophthalmologist", "pediatrician", "psychiatrist",
            "gynecologist", "urologist", "ent", "physiotherapist", "veterinarian",
            "dentistry", "cardiology", "dermatology", "neurology", "orthopedics",
            "ophthalmology", "pediatrics", "psychiatry", "gynecology", "urology"
        }
    
    def validate(
        self,
        department: Optional[str],
        date: Optional[str],
        time: Optional[str]
    ) -> dict:
        """Validate extracted entities and return guardrail status"""
        
        ambiguities = []
        
        if not department or department.lower() not in self.valid_departments:
            ambiguities.append("department")
        
        if not date:
            ambiguities.append("date")
        
        if not time:
            ambiguities.append("time")
        
        if ambiguities:
            return {
                "status": "needs_clarification",
                "message": f"Ambiguous or missing: {', '.join(ambiguities)}. Please provide specific details."
            }
        
        return {
            "status": "ok",
            "message": None
        }
    
    def validate_raw_text(self, text: str) -> dict:
        """Check if raw text is too ambiguous"""
        text_lower = text.lower()
        
        vague_indicators = [
            "sometime", "someday", "whenever", "asap", "soon",
            "later", "maybe", "probably", "possibly"
        ]
        
        for indicator in vague_indicators:
            if indicator in text_lower:
                return {
                    "status": "needs_clarification",
                    "message": f"Vague time indicator '{indicator}' detected. Please provide specific date and time."
                }
        
        return {
            "status": "ok",
            "message": None
        }


guardrail_service = GuardrailService()