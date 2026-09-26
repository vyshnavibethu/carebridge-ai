import re
from typing import Dict, Any, List

DURATION_PATTERNS = [
    r"\b(since\s+yesterday)\b",
    r"\b(started\s+yesterday)\b",
    r"\b(since\s+\w+day)\b",
    r"\b(from\s+last\s+\w+)\b",
    r"\b(started\s+\d+\s+days?\s+ago)\b",
    r"\b(started\s+\d+\s+weeks?\s+ago)\b",
    r"\b(for\s+\d+\s+days?)\b",
    r"\b(for\s+\d+\s+weeks?)\b",
    r"\b(for\s+a\s+week)\b",
    r"\b(for\s+a\s+few\s+days)\b",
    r"\b(for\s+\d+\s+months?)\b",
]

SYMPTOM_LEXICON = {
    "stomach pain": ["stomach pain", "abdominal pain", "belly ache", "stomach ache"],
    "vomiting": ["vomiting", "throwing up", "puking", "emesis"],
    "nausea": ["nausea", "feeling sick", "queasy"],
    "skin rash": ["rash", "skin rash", "red bumps", "hives", "eczema"],
    "itching": ["itching", "itchy skin", "pruritus"],
    "sore throat": ["sore throat", "throat pain", "scratchy throat"],
    "earache": ["earache", "ear pain", "pain in ear"],
    "nasal congestion": ["nasal congestion", "stuffy nose", "blocked nose", "runny nose"],
    "fever": ["fever", "high temperature", "chills"],
    "fatigue": ["fatigue", "tiredness", "exhaustion"],
    "heartburn": ["heartburn", "acid reflux", "chest burning"],
    "sinus pressure": ["sinus pressure", "facial pressure", "sinus pain"]
}

BODY_AREA_MAP = {
    "stomach pain": "Stomach / Abdomen",
    "vomiting": "Stomach / Abdomen",
    "nausea": "Stomach / Abdomen",
    "heartburn": "Stomach / Abdomen & Chest",
    "skin rash": "Skin",
    "itching": "Skin",
    "sore throat": "Throat & Neck",
    "earache": "Ears & Head",
    "nasal congestion": "Nose & Sinuses",
    "sinus pressure": "Head & Sinuses",
    "fever": "Full Body / Systemic",
    "fatigue": "Full Body / Systemic"
}

def extract_duration(text: str) -> str:
    """Extracts duration from user symptom description."""
    text_lower = text.lower()
    for pattern in DURATION_PATTERNS:
        match = re.search(pattern, text_lower, re.IGNORECASE)
        if match:
            found = match.group(1).strip()
            # Capitalize nicely
            return found[0].upper() + found[1:]

    # Generic search for numbers + time units
    match = re.search(r"(\d+\s+(?:day|days|week|weeks|month|months))", text_lower)
    if match:
        return f"For {match.group(1)}"

    return "Not specified"

def extract_symptoms(text: str) -> List[str]:
    """Identifies standard symptom names from user text."""
    text_lower = text.lower()
    detected = []
    for std_name, phrases in SYMPTOM_LEXICON.items():
        for phrase in phrases:
            if phrase in text_lower:
                detected.append(std_name.title())
                break
    return list(dict.fromkeys(detected))

def extract_body_area(symptoms: List[str]) -> str:
    """Infers primary body area from detected symptoms."""
    areas = []
    for s in symptoms:
        s_lower = s.lower()
        if s_lower in BODY_AREA_MAP:
            areas.append(BODY_AREA_MAP[s_lower])
    if areas:
        # Return unique combined string
        return " / ".join(list(dict.fromkeys(areas)))
    return "General / Unspecified"

def extract_trigger(text: str) -> str:
    """Extracts possible reported trigger from text."""
    text_lower = text.lower()
    trigger_patterns = [
        r"after\s+eating\s+([a-zA-Z\s]+)",
        r"after\s+using\s+([a-zA-Z\s]+)",
        r"after\s+([a-zA-Z\s]+)",
        r"triggered\s+by\s+([a-zA-Z\s]+)",
        r"due\s+to\s+([a-zA-Z\s]+)"
    ]
    for pattern in trigger_patterns:
        match = re.search(pattern, text_lower)
        if match:
            extracted = match.group(1).strip()
            # trim after punctuation or stop words
            extracted = re.split(r"[,;.]", extracted)[0]
            return extracted.capitalize()
    return "None reported"

def parse_symptoms(text: str) -> Dict[str, Any]:
    """
    Main Symptom Understanding Agent execution.
    Converts raw patient text into structured symptom details.
    """
    symptoms_list = extract_symptoms(text)
    duration = extract_duration(text)
    body_area = extract_body_area(symptoms_list)
    trigger = extract_trigger(text)

    # Determine chief complaint
    if text:
        # Trim first sentence or main clause for chief complaint
        complaint = text.strip().split(".")[0]
        if len(complaint) > 80:
            complaint = complaint[:77] + "..."
    else:
        complaint = "Unspecified symptoms"

    return {
        "raw_text": text,
        "chief_complaint": complaint,
        "duration": duration,
        "symptoms": symptoms_list if symptoms_list else ["General Discomfort"],
        "possible_trigger": trigger,
        "body_area": body_area,
        "urgency": "Routine"
    }
