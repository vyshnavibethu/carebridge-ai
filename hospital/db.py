import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).parent / "carebridge_hospital.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            experience_years INTEGER NOT NULL,
            qualification TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            rating REAL NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS available_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            slot_time TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id TEXT NOT NULL UNIQUE,
            patient_name TEXT NOT NULL,
            doctor_id INTEGER NOT NULL,
            doctor_name TEXT NOT NULL,
            specialty TEXT NOT NULL,
            slot_time TEXT NOT NULL,
            hospital_name TEXT NOT NULL,
            summary_json TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # Check if doctors are already seeded
    cursor.execute("SELECT COUNT(*) FROM doctors")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_doctors_and_slots(conn)

    conn.close()

def seed_doctors_and_slots(conn):
    cursor = conn.cursor()
    doctors_data = [
        # General Physician
        ("Dr. Sarah Jenkins", "General Physician", 14, "MD - Internal Medicine", "CareBridge Central Hospital", 4.9),
        ("Dr. Rajesh Sharma", "General Physician", 10, "MBBS, MD - General Medicine", "CareBridge Community Clinic", 4.8),

        # Dermatologist
        ("Dr. Elena Rostova", "Dermatologist", 12, "MD - Dermatology & Cutaneous Care", "CareBridge Specialty Skin Care", 4.9),
        ("Dr. Maya Lin", "Dermatologist", 8, "MBBS, DNB - Dermatology", "CareBridge Urban Health", 4.7),

        # Gastroenterologist
        ("Dr. Marcus Vance", "Gastroenterologist", 15, "DM - Gastroenterology", "CareBridge Digestive Health Center", 4.9),
        ("Dr. Anita Roy", "Gastroenterologist", 11, "MD, DNB - Gastroenterology", "CareBridge Central Hospital", 4.8),

        # ENT Specialist
        ("Dr. David Miller", "ENT Specialist", 16, "MS - Otorhinolaryngology (ENT)", "CareBridge ENT & Head-Neck Institute", 4.9),
        ("Dr. Priya Nair", "ENT Specialist", 9, "MBBS, MS - ENT", "CareBridge Community Clinic", 4.7)
    ]

    for doc in doctors_data:
        cursor.execute("""
            INSERT INTO doctors (name, specialty, experience_years, qualification, hospital_name, rating)
            VALUES (?, ?, ?, ?, ?, ?)
        """, doc)
        doctor_id = cursor.lastrowid

        # Seed 4 standard slots for each doctor
        slots = [
            "Today at 10:00 AM",
            "Today at 02:30 PM",
            "Tomorrow at 11:00 AM",
            "Tomorrow at 04:00 PM"
        ]
        for slot in slots:
            cursor.execute("""
                INSERT INTO available_slots (doctor_id, slot_time, is_available)
                VALUES (?, ?, 1)
            """, (doctor_id, slot))

    conn.commit()

if __name__ == "__main__":
    init_db()
    print("Database initialized and seeded successfully.")
