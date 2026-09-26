from pydantic import BaseModel, Field
from typing import List, Optional, Any, Dict

class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "CareBridge Hospital API"

class DoctorSchema(BaseModel):
    id: int
    name: str
    specialty: str
    experience_years: int
    qualification: str
    hospital_name: str
    rating: float

class SlotSchema(BaseModel):
    id: int
    doctor_id: int
    slot_time: str
    is_available: bool

class AppointmentRequest(BaseModel):
    patient_name: str
    doctor_id: int
    slot_time: str
    summary_json: Optional[Dict[str, Any]] = None

class AppointmentResponse(BaseModel):
    booking_id: str
    status: str
    patient_name: str
    doctor_name: str
    specialty: str
    slot_time: str
    hospital_name: str
    confirmation_message: str
