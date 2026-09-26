from typing import Dict, Any

def generate_patient_summary(
    symptoms_info: Dict[str, Any],
    recommended_specialist: str = "General Physician"
) -> Dict[str, Any]:
    """
    Doctor-Facing Summary Agent:
    Generates a structured, standardized summary for healthcare providers.
    """
    chief_complaint = symptoms_info.get("chief_complaint", "Unspecified symptoms")
    duration = symptoms_info.get("duration", "Not specified")
    symptoms = symptoms_info.get("symptoms", [])
    trigger = symptoms_info.get("possible_trigger", "None reported")
    body_area = symptoms_info.get("body_area", "General")
    urgency = symptoms_info.get("urgency", "Routine")

    return {
        "chief_complaint": chief_complaint,
        "duration": duration,
        "symptoms": symptoms,
        "possible_trigger": trigger,
        "body_area": body_area,
        "recommended_specialist": recommended_specialist,
        "urgency": urgency
    }
