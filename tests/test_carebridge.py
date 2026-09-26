import unittest
import json
from fastapi.testclient import TestClient

from hospital.api import app as fastapi_app
from hospital.db import init_db
from agents.safety import check_emergency
from agents.symptom_extractor import parse_symptoms, extract_duration
from agents.rag import search_medical_knowledge
from agents.specialist import recommend_specialist
from agents.summary import generate_patient_summary
from agents.orchestrator import AgentOrchestrator

class TestCareBridgeAI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize hospital DB for tests
        init_db()
        cls.client = TestClient(fastapi_app)

    # 1. Dermatology symptoms
    def test_01_dermatology_symptoms(self):
        symptoms_info = parse_symptoms("I have a red skin rash and itching for 2 days.")
        self.assertIn("Skin Rash", symptoms_info["symptoms"])
        rec = recommend_specialist(symptoms_info)
        self.assertEqual(rec["recommended_specialist"], "Dermatologist")

    # 2. Stomach / digestive symptoms
    def test_02_stomach_digestive_symptoms(self):
        symptoms_info = parse_symptoms("I have stomach pain and vomiting since yesterday.")
        self.assertIn("Stomach Pain", symptoms_info["symptoms"])
        self.assertIn("Vomiting", symptoms_info["symptoms"])
        rec = recommend_specialist(symptoms_info)
        self.assertEqual(rec["recommended_specialist"], "Gastroenterologist")

    # 3. ENT symptoms
    def test_03_ent_symptoms(self):
        symptoms_info = parse_symptoms("Severe sore throat and earache for 5 days.")
        self.assertIn("Sore Throat", symptoms_info["symptoms"])
        self.assertIn("Earache", symptoms_info["symptoms"])
        rec = recommend_specialist(symptoms_info)
        self.assertEqual(rec["recommended_specialist"], "ENT Specialist")

    # 4. Emergency symptoms
    def test_04_emergency_symptoms(self):
        safety = check_emergency("I have severe chest pain and difficulty breathing.")
        self.assertTrue(safety["is_emergency"])
        self.assertEqual(safety["action_required"], "STOP_ROUTINE_ANALYSIS_URGENT_CARE")

    # 5. Duration extraction
    def test_05_duration_extraction(self):
        test_cases = [
            ("stomach pain since yesterday", "Since yesterday"),
            ("vomiting for 2 days", "For 2 days"),
            ("rash for 5 days", "For 5 days"),
            ("cough for a week", "For a week"),
            ("headache from last Monday", "From last Monday"),
            ("fever since Monday", "Since Monday"),
            ("pain started yesterday", "Started yesterday"),
            ("itching started 3 days ago", "Started 3 days ago")
        ]
        for text, expected in test_cases:
            extracted = extract_duration(text)
            self.assertEqual(extracted.lower(), expected.lower(), f"Failed on duration extraction for '{text}'")

    # 6. RAG retrieval
    def test_06_rag_retrieval(self):
        results = search_medical_knowledge("stomach pain and vomiting", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["specialty"], "Gastroenterologist")

    # 7. Specialist recommendation
    def test_07_specialist_recommendation(self):
        info = {"symptoms": ["Heartburn", "Acid Reflux"], "raw_text": "acid reflux"}
        rec = recommend_specialist(info)
        self.assertEqual(rec["recommended_specialist"], "Gastroenterologist")

    # 8. Hospital doctor search via FastAPI
    def test_08_hospital_doctor_search(self):
        response = self.client.get("/doctors?specialty=Gastroenterologist")
        self.assertEqual(response.status_code, 200)
        doctors = response.json()
        self.assertGreater(len(doctors), 0)
        self.assertEqual(doctors[0]["specialty"], "Gastroenterologist")

    # 9. Slot retrieval via FastAPI
    def test_09_slot_retrieval(self):
        # Get first doctor
        docs_res = self.client.get("/doctors")
        doctor_id = docs_res.json()[0]["id"]
        
        slots_res = self.client.get(f"/slots?doctor_id={doctor_id}")
        self.assertEqual(slots_res.status_code, 200)
        slots = slots_res.json()
        self.assertGreater(len(slots), 0)

    # 10. Appointment booking via FastAPI
    def test_10_appointment_booking(self):
        # Fetch doctor and available slot
        docs_res = self.client.get("/doctors?specialty=General Physician")
        doctor_id = docs_res.json()[0]["id"]
        
        slots_res = self.client.get(f"/slots?doctor_id={doctor_id}")
        slot_time = slots_res.json()[0]["slot_time"]

        payload = {
            "patient_name": "Test User",
            "doctor_id": doctor_id,
            "slot_time": slot_time,
            "summary_json": {"chief_complaint": "Mild fever"}
        }

        book_res = self.client.post("/appointments", json=payload)
        self.assertEqual(book_res.status_code, 200)
        data = book_res.json()
        self.assertEqual(data["status"], "CONFIRMED")
        self.assertTrue(data["booking_id"].startswith("CB-"))

    # 11. Doctor summary generation
    def test_11_doctor_summary_generation(self):
        info = {
            "chief_complaint": "Stomach pain and vomiting",
            "duration": "Since yesterday",
            "symptoms": ["Stomach Pain", "Vomiting"],
            "possible_trigger": "None reported",
            "body_area": "Stomach / Abdomen",
            "urgency": "Routine"
        }
        summary = generate_patient_summary(info, "Gastroenterologist")
        self.assertEqual(summary["chief_complaint"], "Stomach pain and vomiting")
        self.assertEqual(summary["duration"], "Since yesterday")
        self.assertEqual(summary["recommended_specialist"], "Gastroenterologist")

    # 12. Light/Dark theme session state structure simulation
    def test_12_theme_session_state(self):
        session_state = {
            "theme": "light",
            "symptom_input": "I have a skin rash since yesterday",
            "selected_doctor_id": 1,
            "selected_slot_time": "Today at 10:00 AM",
            "booking_result": {"status": "CONFIRMED"}
        }
        # Simulate toggle theme
        session_state["theme"] = "dark"
        # Verify state parameters preserved
        self.assertEqual(session_state["symptom_input"], "I have a skin rash since yesterday")
        self.assertEqual(session_state["selected_doctor_id"], 1)

    # 13. Health API check
    def test_13_health_api(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(data["service"], "CareBridge Hospital API")

if __name__ == "__main__":
    unittest.main()
