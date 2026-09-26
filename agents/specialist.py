from typing import Dict, Any, List

SUPPORTED_SPECIALTIES = [
    "General Physician",
    "Dermatologist",
    "Gastroenterologist",
    "ENT Specialist"
]

DERMATOLOGY_KEYWORDS = [
    "rash", "skin redness", "itching", "hives", "eczema", "dry skin", "bumps",
    "skin", "lesion", "blister", "acne", "dermatitis", "pruritus", "erythema"
]

GASTROENTEROLOGY_KEYWORDS = [
    "stomach pain", "abdominal pain", "vomiting", "nausea", "cramping", "indigestion",
    "heartburn", "acid reflux", "diarrhea", "constipation", "bloating", "gastritis", "emesis"
]

ENT_KEYWORDS = [
    "sore throat", "ear ache", "earache", "nasal congestion", "runny nose",
    "sinus pressure", "hoarseness", "throat", "ear pain", "sinus pain", "pharyngitis", "otalgia", "rhinitis"
]

def recommend_specialist(symptoms_info: Dict[str, Any], rag_results: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Identifies the appropriate medical specialist based on symptoms and RAG findings.
    """
    symptoms = [s.lower() for s in symptoms_info.get("symptoms", [])]
    raw_text = symptoms_info.get("raw_text", "").lower()
    combined_text = " ".join(symptoms) + " " + raw_text

    derm_count = sum(1 for kw in DERMATOLOGY_KEYWORDS if kw in combined_text)
    gastro_count = sum(1 for kw in GASTROENTEROLOGY_KEYWORDS if kw in combined_text)
    ent_count = sum(1 for kw in ENT_KEYWORDS if kw in combined_text)

    # Check top match from RAG if available
    if rag_results and len(rag_results) > 0 and rag_results[0].get("relevance_score", 0) > 0.3:
        rag_specialty = rag_results[0].get("specialty")
        if rag_specialty in SUPPORTED_SPECIALTIES:
            return {
                "recommended_specialist": rag_specialty,
                "reasoning": f"Symptoms strongly match {rag_specialty} medical reference profile."
            }

    counts = {
        "Dermatologist": derm_count,
        "Gastroenterologist": gastro_count,
        "ENT Specialist": ent_count
    }

    best_specialty = max(counts, key=counts.get)
    max_score = counts[best_specialty]

    if max_score > 0:
        return {
            "recommended_specialist": best_specialty,
            "reasoning": f"Reported symptoms specifically involve {best_specialty} domain expertise."
        }

    return {
        "recommended_specialist": "General Physician",
        "reasoning": "Symptoms are systemic or general; a General Physician is best suited for initial comprehensive evaluation."
    }
