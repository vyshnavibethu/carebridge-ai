import re
from typing import Dict, Any

EMERGENCY_KEYWORDS = [
    "severe chest pain", "chest pain", "heart attack",
    "difficulty breathing", "shortness of breath", "gasping for air", "cannot breathe", "cant breathe",
    "unconsciousness", "unconscious", "passed out", "blacked out", "fainting",
    "severe bleeding", "heavy bleeding", "bleeding profusely", "hemorrhage",
    "stroke", "facial numbness", "sudden paralysis", "slurred speech", "numbness on one side",
    "severe allergic reaction", "anaphylaxis", "swollen tongue", "throat closing",
    "suicidal thoughts", "suicide", "end my life", "self harm"
]

def check_emergency(text: str) -> Dict[str, Any]:
    """
    Checks if user-described symptoms contain emergency indicators.
    Returns a safety triaging report.
    """
    if not text:
        return {
            "is_emergency": False,
            "detected_keywords": [],
            "warning_message": "",
            "action_required": "Proceed with routine navigation"
        }

    lower_text = text.lower()
    matched_keywords = []

    for kw in EMERGENCY_KEYWORDS:
        if kw in lower_text:
            matched_keywords.append(kw)

    if matched_keywords:
        matched_str = ", ".join([f"'{k}'" for k in set(matched_keywords)])
        warning_msg = (
            "🚨 URGENT MEDICAL EMERGENCY DETECTED!\n\n"
            f"Your input contains signs associated with a medical emergency ({matched_str}).\n"
            "Please call local emergency services immediately (e.g., 911 / 112) or go to the nearest emergency department or urgent care center.\n\n"
            "Routine AI navigation and appointment scheduling have been stopped for your safety."
        )
        return {
            "is_emergency": True,
            "detected_keywords": list(set(matched_keywords)),
            "warning_message": warning_msg,
            "action_required": "STOP_ROUTINE_ANALYSIS_URGENT_CARE"
        }

    return {
        "is_emergency": False,
        "detected_keywords": [],
        "warning_message": "",
        "action_required": "Proceed with routine navigation"
    }
