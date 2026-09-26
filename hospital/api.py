import os
import uuid
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from hospital.db import init_db, get_db_connection
from hospital.models import (
    HealthResponse,
    DoctorSchema,
    SlotSchema,
    AppointmentRequest,
    AppointmentResponse
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize and seed database
    init_db()
    yield
    # Shutdown: nothing to clean up for SQLite

app = FastAPI(
    title="CareBridge Hospital Mock API",
    description="Mock healthcare API for CareBridge AI Smart Navigator",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS using environment variable
frontend_url = os.getenv("FRONTEND_URL", "*")
origins = [frontend_url] if frontend_url != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok", service="CareBridge Hospital API")

@app.get("/doctors", response_model=List[DoctorSchema])
def get_doctors(specialty: Optional[str] = Query(None, description="Filter doctors by medical specialty")):
    conn = get_db_connection()
    cursor = conn.cursor()

    if specialty:
        cursor.execute("SELECT * FROM doctors WHERE LOWER(specialty) = LOWER(?)", (specialty,))
    else:
        cursor.execute("SELECT * FROM doctors")

    rows = cursor.fetchall()
    conn.close()

    doctors = []
    for row in rows:
        doctors.append(DoctorSchema(
            id=row["id"],
            name=row["name"],
            specialty=row["specialty"],
            experience_years=row["experience_years"],
            qualification=row["qualification"],
            hospital_name=row["hospital_name"],
            rating=row["rating"]
        ))
    return doctors

@app.get("/slots", response_model=List[SlotSchema])
def get_slots(doctor_id: int = Query(..., description="ID of the doctor")):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM available_slots 
        WHERE doctor_id = ? AND is_available = 1
    """, (doctor_id,))

    rows = cursor.fetchall()
    conn.close()

    slots = []
    for row in rows:
        slots.append(SlotSchema(
            id=row["id"],
            doctor_id=row["doctor_id"],
            slot_time=row["slot_time"],
            is_available=bool(row["is_available"])
        ))
    return slots

@app.post("/appointments", response_model=AppointmentResponse)
def book_appointment(req: AppointmentRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verify doctor exists
    cursor.execute("SELECT * FROM doctors WHERE id = ?", (req.doctor_id,))
    doctor = cursor.fetchone()
    if not doctor:
        conn.close()
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Verify slot is available
    cursor.execute("""
        SELECT * FROM available_slots 
        WHERE doctor_id = ? AND slot_time = ? AND is_available = 1
    """, (req.doctor_id, req.slot_time))
    slot = cursor.fetchone()
    if not slot:
        conn.close()
        raise HTTPException(status_code=400, detail="Requested slot is not available or already booked")

    # Generate unique booking ID
    booking_id = f"CB-{uuid.uuid4().hex[:8].upper()}"

    # Mark slot as unavailable
    cursor.execute("""
        UPDATE available_slots 
        SET is_available = 0 
        WHERE id = ?
    """, (slot["id"],))

    # Insert appointment record
    summary_str = json.dumps(req.summary_json) if req.summary_json else "{}"
    cursor.execute("""
        INSERT INTO appointments (booking_id, patient_name, doctor_id, doctor_name, specialty, slot_time, hospital_name, summary_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        booking_id,
        req.patient_name,
        doctor["id"],
        doctor["name"],
        doctor["specialty"],
        req.slot_time,
        doctor["hospital_name"],
        summary_str
    ))

    conn.commit()
    conn.close()

    return AppointmentResponse(
        booking_id=booking_id,
        status="CONFIRMED",
        patient_name=req.patient_name,
        doctor_name=doctor["name"],
        specialty=doctor["specialty"],
        slot_time=req.slot_time,
        hospital_name=doctor["hospital_name"],
        confirmation_message=f"Appointment successfully confirmed with {doctor['name']} ({doctor['specialty']}) for {req.slot_time} at {doctor['hospital_name']}."
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
