# CareBridge AI – Smart Healthcare Navigator 🩺

CareBridge AI is a privacy-first, empathetic AI healthcare navigation assistant designed for college projects and medical navigation demonstrations. It analyzes user-described symptoms, performs safety triaging, retrieves verified medical information using RAG, identifies appropriate specialist domains, interacts with a mock hospital REST API to discover doctors and available slots, allows explicit appointment booking, and generates structured doctor-facing summaries.

> ⚠️ **IMPORTANT SAFETY & NON-DIAGNOSIS DISCLAIMER**
> CareBridge AI does **NOT** diagnose medical conditions and does **NOT** prescribe medicines. It provides educational guidance, triaging recommendations, and specialist navigation. If emergency symptoms are detected, routine booking stops immediately and urgent care guidance is provided.

---

## 🌟 Key Features

1. **8-Stage Agentic Workflow Pipeline:** Real multi-agent execution orchestrating symptom extraction, safety triaging, RAG search, specialist matching, doctor lookup, slot management, booking, and summary formatting.
2. **Safety & Emergency Triaging:** Automatic detection of red-flag symptoms (severe chest pain, difficulty breathing, stroke signs, severe bleeding, suicidal thoughts, anaphylaxis) which halts routine scheduling to advise emergency care.
3. **Scikit-Learn RAG Medical Retrieval:** Vector similarity search querying `medical_knowledge.json` for verified medical info, 8th-grade explanations, key terms, and source citations (CDC, Mayo Clinic, WHO, PubMed).
4. **FastAPI Mock Hospital Backend:** REST API backed by an SQLite database managing doctors across 4 supported specialties (*General Physician, Dermatologist, Gastroenterologist, ENT Specialist*), slot availability, and confirmed appointments.
5. **PDF Lab Report Analyzer:** PyPDF parser extracting test parameters from blood work / lab reports with non-prescriptive, simple explanations.
6. **Responsive Dual-Theme UI:** Streamlit interface with a seamless Light/Dark mode toggle maintaining session state across theme changes.
7. **Doctor-Facing Patient Summary Card:** Structured intake summary JSON viewer for healthcare providers.

---

## 🏗️ Architecture & Agentic Workflow

```
               User Symptoms Input
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 1. Symptom Understanding Agent   │ (Extracts complaint, duration, trigger, body area)
      └─────────────────┬─────────────────┘
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 2. Safety / Emergency Agent       │
      └─────────────────┬─────────────────┘
                        │
         Is Emergency? ─┼───────────────────► YES: Show Urgent Care Alert & STOP routine flow
                        │ NO
                        ▼
      ┌───────────────────────────────────┐
      │ 3. Medical Knowledge RAG Tool     │ (TF-IDF Similarity Search in medical_knowledge.json)
      └─────────────────┬─────────────────┘
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 4. Specialist Recommender Agent   │ (Matches General Physician, Derm, Gastro, or ENT)
      └─────────────────┬─────────────────┘
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 5. Hospital API -> Find Doctors   │ (GET /doctors?specialty=...)
      └─────────────────┬─────────────────┘
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 6. Hospital API -> Get Slots      │ (GET /slots?doctor_id=...)
      └─────────────────┬─────────────────┘
                        │
             User Selects Doctor & Slot
                        │
             Clicks "Confirm Appointment"
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 7. Hospital API -> Book           │ (POST /appointments)
      └─────────────────┬─────────────────┘
                        │
                        ▼
      ┌───────────────────────────────────┐
      │ 8. Doctor Summary Generator Agent │ (Structured JSON Summary Card)
      └───────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend API:** FastAPI & Uvicorn
- **Database:** SQLite (`carebridge_hospital.db`)
- **RAG Vector Search:** Scikit-Learn (TF-IDF & Cosine Similarity)
- **PDF Report Parsing:** PyPDF
- **HTTP Client:** Requests
- **Config:** python-dotenv, Pydantic

---

## 🚀 Local Setup Instructions

### 1. Clone & Navigate to Project
```bash
git clone https://github.com/your-username/carebridge-ai.git
cd carebridge-ai
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Default `.env` contents:
```env
HOSPITAL_API_URL=http://127.0.0.1:8000
FRONTEND_URL=*
PORT=8000
```

---

## 🖥️ Running the Application Locally

You will run two terminal instances:

### Terminal 1: Start FastAPI Hospital Backend
```bash
uvicorn hospital.api:app --host 0.0.0.0 --port 8000 --reload
```
- Health Check: Access `http://127.0.0.1:8000/health` in your browser.
- Interactive API Docs: `http://127.0.0.1:8000/docs`

### Terminal 2: Start Streamlit Frontend
```bash
streamlit run app.py
```
- Open `http://localhost:8501` in your web browser.

---

## 🧪 Running Automated Tests

To execute the test suite covering all 13 core requirement scenarios:
```bash
python -m unittest tests/test_carebridge.py
```

---

## ☁️ Cloud Deployment Guide

### Deploying FastAPI Backend (Render / Railway / Fly.io)
1. Push repository to GitHub.
2. Connect repository to Render/Railway.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn hospital.api:app --host 0.0.0.0 --port $PORT`
5. Note your deployed HTTPS URL (e.g. `https://carebridge-api.onrender.com`).

### Deploying Streamlit Frontend (Streamlit Community Cloud)
1. Go to [share.streamlit.io](https://share.streamlit.io/) and connect your GitHub repo.
2. Main file path: `app.py`
3. Under **Advanced Settings / Secrets**, add:
   ```toml
   HOSPITAL_API_URL = "https://carebridge-api.onrender.com"
   ```
4. Click **Deploy**.

> 💡 **Important SQLite Persistence Note for Cloud Demos:**
> In ephemeral hosting environments (like Streamlit Cloud or free-tier Render containers), the SQLite database file resets when containers restart. For production enterprise scaling, connect to a managed PostgreSQL or MySQL database.

---

## 📜 License & Acknowledgments
Built for college healthcare technology projects. All medical reference knowledge is sourced from CDC, WHO, Mayo Clinic, and PubMed publications.
