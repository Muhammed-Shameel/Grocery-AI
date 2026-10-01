import re
import logging

logger = logging.getLogger(__name__)

class SecurityGuardrail:
    """Validates user input against prompt injection and malicious patterns."""
    
    INJECTION_PATTERNS = [
        r"ignore previous instructions",
        r"system prompt",
        r"you are now",
        r"disregard all rules",
        r"reveal your prompt"
    ]

    def validate(self, text: str) -> dict:
        if not text or not isinstance(text, str):
            return {"is_safe": True, "sanitized_text": ""}
        
        lower_text = text.lower()
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, lower_text):
                logger.warning(f"Potential prompt injection detected matching pattern: {pattern}")
                return {
                    "is_safe": False,
                    "sanitized_text": "I am a grocery AI assistant. I cannot fulfill instructions that override my safety guidelines.",
                    "reason": "Potential prompt injection detected."
                }
        
        return {"is_safe": True, "sanitized_text": text}
