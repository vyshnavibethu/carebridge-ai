from typing import Dict, Any, List, Optional

from agents.symptom_extractor import parse_symptoms
from agents.safety import check_emergency
from agents.rag import search_medical_knowledge
from agents.specialist import recommend_specialist
from agents.hospital_client import find_doctors, get_available_slots, book_appointment
from agents.summary import generate_patient_summary

class AgentOrchestrator:
    """
    Agent Orchestrator controlling the 8-step healthcare navigation workflow
    and maintaining structured execution state.
    """
    def __init__(self, api_url: Optional[str] = None):
        self.api_url = api_url

    def analyze_symptoms(self, symptom_text: str) -> Dict[str, Any]:
        """
        Executes Steps 1 through 6 of the routine agent workflow:
        1. Symptom Understanding
        2. Safety / Emergency Check
        3. Medical Knowledge RAG Retrieval
        4. Specialist Recommendation
        5. Find Hospital Doctors
        6. Fetch Doctor Available Slots
        """
        activity_log = []
        state = {
            "symptoms_text": symptom_text,
            "activity_log": activity_log,
            "is_emergency": False,
            "emergency_report": None,
            "symptoms_info": None,
            "rag_results": [],
            "specialist_info": None,
            "doctors": [],
            "patient_summary": None,
            "step_completed": False
        }

        if not symptom_text or not symptom_text.strip():
            return state

        # Step 1: Symptom Understanding Agent
        symptoms_info = parse_symptoms(symptom_text)
        state["symptoms_info"] = symptoms_info
        activity_log.append("✓ Symptoms understood")

        # Step 2: Safety / Emergency Agent
        safety_report = check_emergency(symptom_text)
        state["emergency_report"] = safety_report
        activity_log.append("✓ Safety check completed")

        if safety_report["is_emergency"]:
            state["is_emergency"] = True
            # STOP routine analysis and booking
            return state

        # Step 3: Medical Knowledge RAG Tool
        rag_results = search_medical_knowledge(symptom_text, top_k=2)
        state["rag_results"] = rag_results
        activity_log.append("✓ Medical knowledge retrieved")

        # Step 4: Specialist Recommendation Agent
        specialist_info = recommend_specialist(symptoms_info, rag_results)
        state["specialist_info"] = specialist_info
        activity_log.append("✓ Specialist identified")

        # Step 5: Hospital API -> Find Doctors
        rec_specialty = specialist_info["recommended_specialist"]
        doctors = find_doctors(specialty=rec_specialty, api_url=self.api_url)
        state["doctors"] = doctors
        activity_log.append("✓ Hospital doctors searched")

        # Step 6: Doctor slots will be fetched dynamically when user selects a doctor in UI
        # Step 8 Summary pre-generation
        patient_summary = generate_patient_summary(symptoms_info, rec_specialty)
        state["patient_summary"] = patient_summary
        activity_log.append("✓ Doctor summary generated")

        state["step_completed"] = True
        return state

    def fetch_doctor_slots(self, doctor_id: int) -> List[Dict[str, Any]]:
        """Fetch slots for doctor via Hospital API."""
        return get_available_slots(doctor_id, api_url=self.api_url)

    def confirm_booking(
        self,
        patient_name: str,
        doctor_id: int,
        slot_time: str,
        patient_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes Step 7: Book Appointment via Hospital API POST endpoint.
        """
        result = book_appointment(
            patient_name=patient_name,
            doctor_id=doctor_id,
            slot_time=slot_time,
            patient_summary=patient_summary,
            api_url=self.api_url
        )
        return result
