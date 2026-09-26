import os
import requests
from typing import List, Dict, Any

DEFAULT_API_URL = os.getenv("HOSPITAL_API_URL", "http://127.0.0.1:8000")

def get_base_url(api_url: str = None) -> str:
    url = api_url or os.getenv("HOSPITAL_API_URL") or DEFAULT_API_URL
    return url.rstrip("/")

def check_hospital_health(api_url: str = None) -> bool:
    """Checks if the FastAPI hospital backend is responsive."""
    base_url = get_base_url(api_url)
    try:
        res = requests.get(f"{base_url}/health", timeout=3)
        return res.status_code == 200 and res.json().get("status") == "ok"
    except Exception:
        return False

def find_doctors(specialty: str = None, api_url: str = None) -> List[Dict[str, Any]]:
    """
    Hospital API Client: Retrieves doctors for a given specialty.
    """
    base_url = get_base_url(api_url)
    params = {}
    if specialty:
        params["specialty"] = specialty

    try:
        res = requests.get(f"{base_url}/doctors", params=params, timeout=5)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"Error fetching doctors from {base_url}/doctors: {e}")
        return []

def get_available_slots(doctor_id: int, api_url: str = None) -> List[Dict[str, Any]]:
    """
    Hospital API Client: Retrieves available time slots for a given doctor ID.
    """
    base_url = get_base_url(api_url)
    try:
        res = requests.get(f"{base_url}/slots", params={"doctor_id": doctor_id}, timeout=5)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"Error fetching slots from {base_url}/slots: {e}")
        return []

def book_appointment(
    patient_name: str,
    doctor_id: int,
    slot_time: str,
    patient_summary: Dict[str, Any] = None,
    api_url: str = None
) -> Dict[str, Any]:
    """
    Hospital API Client: Books an appointment with the selected doctor and slot.
    Sends POST request to /appointments.
    """
    base_url = get_base_url(api_url)
    payload = {
        "patient_name": patient_name,
        "doctor_id": doctor_id,
        "slot_time": slot_time,
        "summary_json": patient_summary or {}
    }

    try:
        res = requests.post(f"{base_url}/appointments", json=payload, timeout=5)
        if res.status_code == 200:
            return res.json()
        else:
            return {
                "error": True,
                "status_code": res.status_code,
                "message": res.json().get("detail", "Failed to book appointment")
            }
    except Exception as e:
        return {
            "error": True,
            "message": f"Connection error calling {base_url}/appointments: {str(e)}"
        }
