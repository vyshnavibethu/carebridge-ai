import os
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from agents.orchestrator import AgentOrchestrator
from agents.pdf_reader import analyze_pdf_report
from agents.hospital_client import check_hospital_health, find_doctors, get_available_slots

# Page configuration
st.set_page_config(
    page_title="CareBridge AI – Smart Healthcare Navigator",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Environment variables
API_URL = os.getenv("HOSPITAL_API_URL", "http://127.0.0.1:8000")

# Session State Initialization (Theme and Workflow state)
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

if "symptom_input" not in st.session_state:
    st.session_state["symptom_input"] = ""

if "patient_name" not in st.session_state:
    st.session_state["patient_name"] = "Patient"

if "analysis_state" not in st.session_state:
    st.session_state["analysis_state"] = None

if "selected_doctor_id" not in st.session_state:
    st.session_state["selected_doctor_id"] = None

if "selected_slot_time" not in st.session_state:
    st.session_state["selected_slot_time"] = None

if "booking_result" not in st.session_state:
    st.session_state["booking_result"] = None


# Theme CSS injection function
def get_theme_css(theme: str) -> str:
    if theme == "dark":
        bg_color = "#0B1220"
        card_bg = "#1E293B"
        main_text = "#F8FAFC"
        sec_text = "#CBD5E1"
        muted_text = "#94A3B8"
        border_color = "#334155"
        input_bg = "#0F172A"
        input_text = "#F8FAFC"
        badge_bg = "#1E3A8A"
        badge_text = "#93C5FD"
    else:
        bg_color = "#F0F4F8"
        card_bg = "#FFFFFF"
        main_text = "#0F172A"
        sec_text = "#475569"
        muted_text = "#64748B"
        border_color = "#E2E8F0"
        input_bg = "#FFFFFF"
        input_text = "#0F172A"
        badge_bg = "#E0F2FE"
        badge_text = "#0369A1"

    return f"""
    <style>
        /* Base App Styling */
        .stApp {{
            background-color: {bg_color};
            color: {main_text};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }}
        
        /* Main Container Cards */
        .cb-card {{
            background-color: {card_bg};
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        }}
        
        /* Headers & Typography */
        .cb-title {{
            color: {main_text};
            font-size: 1.35rem;
            font-weight: 700;
            margin-bottom: 12px;
        }}
        
        .cb-subtext {{
            color: {sec_text};
            font-size: 0.95rem;
            line-height: 1.5;
        }}
        
        .cb-muted {{
            color: {muted_text};
            font-size: 0.85rem;
        }}

        .cb-badge {{
            display: inline-block;
            background-color: {badge_bg};
            color: {badge_text};
            padding: 4px 12px;
            border-radius: 9999px;
            font-size: 0.85rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}

        /* Activity Checklist Item */
        .cb-activity-item {{
            color: #10B981;
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Streamlit widget contrast overrides */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stSelectbox > div > div > div {{
            background-color: {input_bg} !important;
            color: {input_text} !important;
            border-color: {border_color} !important;
        }}

        .stButton > button {{
            background: linear-gradient(135deg, #0284C7 0%, #0D9488 100%) !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 600 !important;
            transition: all 0.2s ease !important;
        }}

        .stButton > button:hover {{
            opacity: 0.9 !important;
            transform: translateY(-1px) !important;
        }}
        
        /* Alert Containers */
        .stAlert {{
            border-radius: 8px;
        }}
    </style>
    """

# Apply Theme CSS
st.markdown(get_theme_css(st.session_state["theme"]), unsafe_allow_html=True)

# Instantiate Orchestrator
orchestrator = AgentOrchestrator(api_url=API_URL)

# --- HEADER SECTION ---
col_head, col_theme = st.columns([4, 1])

with col_head:
    st.title("🩺 CareBridge AI")
    st.caption("Smart Healthcare Navigator – Privacy-First & Empathetic AI Triage")

with col_theme:
    st.write(" ") # alignment spacer
    theme_choice = st.radio(
        "🎨 Appearance",
        options=["☀️ Light", "🌙 Dark"],
        index=0 if st.session_state["theme"] == "light" else 1,
        key="theme_toggle_radio",
        horizontal=True
    )
    new_theme = "light" if "Light" in theme_choice else "dark"
    if new_theme != st.session_state["theme"]:
        st.session_state["theme"] = new_theme
        st.rerun()

st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("🏥 Hospital Connection")
    
    # Check Hospital API Health
    is_api_healthy = check_hospital_health(API_URL)
    if is_api_healthy:
        st.success(f"Backend Connected\n`{API_URL}`")
    else:
        st.error(f"Backend Disconnected\n`{API_URL}`\nPlease start FastAPI server.")

    st.markdown("---")
    st.header("🔒 Privacy Notice")
    st.info(
        "CareBridge AI is a demonstration healthcare navigator. "
        "Please avoid entering unnecessary personally identifying information (such as SSN, full home address, or government IDs). "
        "All data processed remains private within this demo environment."
    )
    
    st.markdown("---")
    st.markdown("### 📋 Supported Specialties")
    st.markdown("- 👨‍⚕️ General Physician")
    st.markdown("- 🩺 Dermatologist")
    st.markdown("- 🫁 Gastroenterologist")
    st.markdown("- 👂 ENT Specialist")

    st.markdown("---")
    st.caption("© CareBridge AI Healthcare Navigator")

# --- MAIN NAVIGATION TABS ---
tab_nav, tab_lab, tab_about = st.tabs([
    "🩺 Symptom Navigator & Booking",
    "📄 Lab Report Analyzer (PDF)",
    "ℹ️ About & Safety Disclaimer"
])

# ==========================================
# TAB 1: SYMPTOM NAVIGATOR & BOOKING
# ==========================================
with tab_nav:
    st.markdown("### Describe Your Symptoms")
    st.markdown(
        "Describe what you are feeling in your own words. Include how long it has been happening "
        "(e.g., *'since yesterday'*, *'for 2 days'*, *'started 3 days ago'*)."
    )

    with st.form("symptom_form"):
        symptom_input = st.text_area(
            "Symptoms & Duration",
            value=st.session_state["symptom_input"],
            placeholder="Example: I have stomach pain and vomiting since yesterday after eating dinner.",
            height=110
        )
        patient_name_input = st.text_input(
            "Your Name (for appointment booking)",
            value=st.session_state["patient_name"]
        )
        
        col_btn, _ = st.columns([1, 4])
        with col_btn:
            submit_btn = st.form_submit_button("Analyze Symptoms & Navigate 🚀")

    if submit_btn and symptom_input.strip():
        st.session_state["symptom_input"] = symptom_input
        st.session_state["patient_name"] = patient_name_input or "Patient"
        st.session_state["booking_result"] = None
        st.session_state["selected_doctor_id"] = None
        st.session_state["selected_slot_time"] = None
        
        # Execute Orchestrator Workflow
        with st.spinner("AI Agents analyzing symptoms, triaging safety, and retrieving medical knowledge..."):
            st.session_state["analysis_state"] = orchestrator.analyze_symptoms(symptom_input)

    # DISPLAY RESULTS IF ANALYSIS EXISTS
    analysis_state = st.session_state.get("analysis_state")

    if analysis_state:
        st.markdown("---")
        
        # --- AI AGENT ACTIVITY CHECKLIST ---
        st.markdown("#### 🤖 AI Agent Execution Pipeline")
        activity_cols = st.columns(len(analysis_state["activity_log"]) if analysis_state["activity_log"] else 1)
        
        activity_html = "<div style='display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 20px;'>"
        for step in analysis_state["activity_log"]:
            activity_html += f"<div class='cb-badge'>{step}</div>"
        activity_html += "</div>"
        st.markdown(activity_html, unsafe_allow_html=True)

        # --- STEP 2: EMERGENCY CHECK RESULT ---
        if analysis_state["is_emergency"]:
            report = analysis_state["emergency_report"]
            st.error(report["warning_message"])
            st.warning(
                "⚠️ **Booking Suspended:** Routine appointment scheduling is unavailable for emergency conditions. "
                "Please proceed directly to urgent medical care."
            )
        else:
            # --- ROUTINE RESULTS DISPLAY ---
            
            # 1. RAG Medical Results (5 Cards Format)
            st.markdown("### 📚 Medical Knowledge Guidance")
            
            rag_results = analysis_state.get("rag_results", [])
            symptoms_info = analysis_state.get("symptoms_info", {})
            
            if rag_results:
                primary_match = rag_results[0]
                
                # Card 1: What symptoms may be associated with
                st.markdown(f"""
                <div class='cb-card'>
                    <div class='cb-title'>1. What symptoms may be associated with</div>
                    <div class='cb-subtext'>Your reported symptoms of <strong>{', '.join(symptoms_info.get('symptoms', ['general discomfort']))}</strong> ({symptoms_info.get('duration', 'Duration unstated')}) can sometimes be associated with:</div>
                    <ul style='margin-top: 10px; color: inherit;'>
                        {''.join([f"<li>{exp}</li>" for exp in primary_match.get('possible_explanations', [])])}
                    </ul>
                </div>
                """, unsafe_allow_html=True)

                # Card 2: Simple Explanation
                st.markdown(f"""
                <div class='cb-card'>
                    <div class='cb-title'>2. Simple Explanation (8th-Grade Level)</div>
                    <div class='cb-subtext'>{primary_match.get('simple_explanation')}</div>
                </div>
                """, unsafe_allow_html=True)

                # Card 3: Medical Terms
                med_terms = primary_match.get('medical_terms', {})
                terms_html = "".join([f"<li><strong>{k}:</strong> {v}</li>" for k, v in med_terms.items()])
                st.markdown(f"""
                <div class='cb-card'>
                    <div class='cb-title'>3. Key Medical Terminology</div>
                    <ul style='margin-top: 5px;'>{terms_html}</ul>
                </div>
                """, unsafe_allow_html=True)

                # Card 4: General Guidance & Source Citation
                st.markdown(f"""
                <div class='cb-card'>
                    <div class='cb-title'>4. General Non-Prescriptive Guidance</div>
                    <div class='cb-subtext'>{primary_match.get('general_guidance')}</div>
                    <hr style='margin: 15px 0; border-color: rgba(128,128,128,0.2);'>
                    <div class='cb-muted'>📖 <strong>Source Citation:</strong> {primary_match.get('source_name')} | <a href='{primary_match.get("source_url")}' target='_blank'>View Medical Source Reference</a></div>
                </div>
                """, unsafe_allow_html=True)

                # Card 5: Safety & Non-Diagnosis Disclaimer
                st.markdown("""
                <div class='cb-card' style='border-left: 4px solid #0284C7;'>
                    <div class='cb-title'>5. Safety & Non-Diagnosis Reminder</div>
                    <div class='cb-subtext'>
                        ⚠️ <strong>Important Notice:</strong> CareBridge AI provides educational information and triaging navigation. 
                        <strong>This is not a diagnosis and we do not prescribe medicines.</strong> Please consult a qualified healthcare professional for medical diagnosis and treatment.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # --- DOCTOR-FACING SUMMARY CARD ---
            st.markdown("### 📋 Doctor-Facing Patient Summary")
            patient_summary = analysis_state.get("patient_summary", {})
            
            c_sum1, c_sum2 = st.columns([3, 2])
            with c_sum1:
                st.markdown(f"""
                <div class='cb-card'>
                    <div class='cb-title'>Structured Patient Intake Summary</div>
                    <div class='cb-subtext'>
                        • <strong>Chief Complaint:</strong> {patient_summary.get('chief_complaint')}<br>
                        • <strong>Duration:</strong> {patient_summary.get('duration')}<br>
                        • <strong>Symptoms:</strong> {', '.join(patient_summary.get('symptoms', []))}<br>
                        • <strong>Possible Trigger:</strong> {patient_summary.get('possible_trigger')}<br>
                        • <strong>Body Area:</strong> {patient_summary.get('body_area')}<br>
                        • <strong>Recommended Specialist:</strong> <span style='color: #0284C7; font-weight: 700;'>{patient_summary.get('recommended_specialist')}</span><br>
                        • <strong>Triage Urgency:</strong> {patient_summary.get('urgency')}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with c_sum2:
                with st.expander("🔍 View Raw JSON Summary Object"):
                    st.json(patient_summary)

            # --- HOSPITAL DOCTOR SEARCH & SLOT BOOKING ---
            st.markdown("---")
            st.markdown("### 👨‍⚕️ Available Doctors & Appointment Booking")

            specialist_info = analysis_state.get("specialist_info", {})
            rec_specialty = specialist_info.get("recommended_specialist", "General Physician")
            doctors = analysis_state.get("doctors", [])

            st.info(f"💡 Recommended Specialist Domain: **{rec_specialty}** ({specialist_info.get('reasoning')})")

            if not is_api_healthy:
                st.error("Hospital API server is currently unreachable. Please start FastAPI (`uvicorn hospital.api:app --port 8000`) to book appointments.")
            elif not doctors:
                st.warning(f"No doctors found for specialty: {rec_specialty}")
            else:
                # Doctor Selection Dropdown/Radio
                doc_options = {doc["id"]: f"{doc['name']} ({doc['qualification']}) - {doc['hospital_name']} | Rating: ⭐ {doc['rating']}" for doc in doctors}
                
                selected_doc_id = st.selectbox(
                    "Select a Doctor",
                    options=list(doc_options.keys()),
                    format_func=lambda x: doc_options[x],
                    key="doctor_select_box"
                )
                
                st.session_state["selected_doctor_id"] = selected_doc_id
                
                # Fetch slots dynamically for selected doctor
                available_slots = orchestrator.fetch_doctor_slots(selected_doc_id)

                if available_slots:
                    slot_times = [s["slot_time"] for s in available_slots]
                    selected_slot = st.radio(
                        "Available Appointment Slots",
                        options=slot_times,
                        key="slot_radio_select"
                    )
                    st.session_state["selected_slot_time"] = selected_slot
                    
                    st.markdown(" ")
                    col_confirm, _ = st.columns([2, 3])
                    with col_confirm:
                        confirm_booking_btn = st.button("Explicit Confirm Appointment 📅")

                    if confirm_booking_btn:
                        with st.spinner("Booking appointment via Hospital API POST /appointments..."):
                            booking_res = orchestrator.confirm_booking(
                                patient_name=st.session_state["patient_name"],
                                doctor_id=selected_doc_id,
                                slot_time=selected_slot,
                                patient_summary=patient_summary
                            )
                            st.session_state["booking_result"] = booking_res

                    # DISPLAY BOOKING CONFIRMATION IF BOOKED
                    booking_res = st.session_state.get("booking_result")
                    if booking_res:
                        if booking_res.get("error"):
                            st.error(f"Booking Error: {booking_res.get('message')}")
                        else:
                            # Update Activity Checklist to include Booking Confirmed
                            if "✓ Appointment confirmed" not in analysis_state["activity_log"]:
                                analysis_state["activity_log"].append("✓ Available slots retrieved")
                                analysis_state["activity_log"].append("✓ Appointment confirmed")
                            
                            st.balloons()
                            st.success(f"🎉 **Appointment Successfully Confirmed!**")
                            st.markdown(f"""
                            <div class='cb-card' style='border-left: 4px solid #10B981;'>
                                <div class='cb-title' style='color: #10B981;'>Booking ID: {booking_res.get('booking_id')}</div>
                                <div class='cb-subtext'>
                                    • <strong>Patient Name:</strong> {booking_res.get('patient_name')}<br>
                                    • <strong>Doctor:</strong> {booking_res.get('doctor_name')} ({booking_res.get('specialty')})<br>
                                    • <strong>Hospital:</strong> {booking_res.get('hospital_name')}<br>
                                    • <strong>Scheduled Slot:</strong> {booking_res.get('slot_time')}<br>
                                    • <strong>Status:</strong> <span style='color: #10B981; font-weight: bold;'>CONFIRMED</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                else:
                    st.warning("No available time slots for this doctor at the moment.")

# ==========================================
# TAB 2: LAB REPORT ANALYZER (PDF)
# ==========================================
with tab_nav:
    pass # Managed via tabs context below

with tab_lab:
    st.markdown("### 📄 Blood Test & Lab Report Analyzer")
    st.markdown(
        "Upload a text-based medical lab report PDF. CareBridge AI will extract parameters "
        "and provide simple 8th-grade explanations for detected terms and reference ranges."
    )
    
    uploaded_pdf = st.file_uploader("Upload Lab Report (PDF)", type=["pdf"])
    
    if uploaded_pdf is not None:
        pdf_bytes = uploaded_pdf.read()
        with st.spinner("Parsing PDF using PyPDF and extracting lab parameters..."):
            lab_result = analyze_pdf_report(pdf_bytes)
            
        if not lab_result.get("success"):
            st.error(lab_result.get("message"))
        else:
            st.success("Lab report successfully processed!")
            
            with st.expander("📄 View Extracted Text Snippet from PDF"):
                st.code(lab_result.get("extracted_text_snippet", ""))

            detected_tests = lab_result.get("detected_tests", [])
            if detected_tests:
                st.markdown("#### Detected Lab Parameters & Simple Explanations")
                for test in detected_tests:
                    st.markdown(f"""
                    <div class='cb-card'>
                        <div class='cb-title'>🧪 {test['name']}</div>
                        <div class='cb-subtext'>
                            • <strong>Role in Body:</strong> {test['role']}<br>
                            • <strong>Simple Explanation:</strong> {test['low_explanation']}<br>
                            • <strong>General Dietary Sources:</strong> {test['dietary_sources']}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info(lab_result.get("summary_explanation"))

            st.warning(
                "⚠️ **Disclaimer:** This PDF report analyzer is for educational reference only. "
                "It does not perform OCR on scanned image PDFs, and does NOT replace professional medical diagnosis."
            )

# ==========================================
# TAB 3: ABOUT & DISCLAIMERS
# ==========================================
with tab_about:
    st.markdown("### About CareBridge AI")
    st.markdown("""
    **CareBridge AI** is a privacy-first, empathetic AI healthcare navigation assistant designed for college and clinical demo projects.
    
    #### Key Features & Architecture:
    - **8-Stage Agent Pipeline:** Real multi-agent orchestration handling symptom extraction, safety triaging, RAG retrieval, specialist matching, hospital API calls, and doctor summary creation.
    - **RAG Medical Knowledge Retrieval:** Scikit-Learn TF-IDF vector search querying verified medical references.
    - **FastAPI Mock Hospital Backend:** Dynamic REST API with SQLite database supporting `/health`, `/doctors`, `/slots`, and `/appointments`.
    - **PyPDF Report Parsing:** Non-prescriptive lab report analysis.
    - **Privacy First:** No storage of sensitive PII; non-diagnostic guidance language.
    """)
    st.markdown("---")
    st.info("Emergency Hotlines: In case of life-threatening emergencies, dial **911** (US), **112** (Europe/India), or visit your nearest emergency room.")
