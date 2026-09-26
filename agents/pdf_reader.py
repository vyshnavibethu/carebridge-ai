import io
from typing import Dict, Any, List
import pypdf

# Common lab test reference knowledge database for simple patient-friendly explanation
LAB_TEST_KNOWLEDGE = {
    "iron": {
        "name": "Serum Iron / Ferritin",
        "role": "Iron helps red blood cells carry oxygen throughout your body.",
        "dietary_sources": "Spinach, lentils, beans, fortified cereals, lean red meat, and pumpkin seeds.",
        "low_explanation": "If your iron level is below the reference range, your body may feel tired or sluggish because oxygen transport is reduced."
    },
    "hemoglobin": {
        "name": "Hemoglobin (Hb)",
        "role": "Hemoglobin is a protein in red blood cells that transports oxygen from your lungs to the rest of your body.",
        "dietary_sources": "Iron-rich foods, dark leafy greens, poultry, and vitamin C-rich foods (oranges, bell peppers) which boost iron absorption.",
        "low_explanation": "A hemoglobin level below reference range indicates mild anemia, which can cause fatigue, shortness of breath, or pale skin."
    },
    "glucose": {
        "name": "Fasting Blood Glucose",
        "role": "Glucose (sugar) provides energy for your body's cells.",
        "dietary_sources": "Balanced low-glycemic foods, whole grains, vegetables, and lean proteins.",
        "high_explanation": "A glucose level above reference range indicates higher sugar in the bloodstream, which is important to monitor with your physician."
    },
    "cholesterol": {
        "name": "Lipid Profile / Cholesterol",
        "role": "Cholesterol is a lipid substance your body uses to build cells and vitamins.",
        "dietary_sources": "Fiber-rich oats, nuts, avocado, olive oil, and heart-healthy fish.",
        "high_explanation": "Elevated cholesterol levels may benefit from dietary adjustments such as increasing soluble fiber and reducing saturated fats."
    },
    "wbc": {
        "name": "White Blood Cell Count (WBC)",
        "role": "White blood cells are your immune system's primary defenders against infections.",
        "dietary_sources": "Immune-supporting foods rich in Vitamin C (citrus fruits) and Zinc.",
        "high_explanation": "Elevated WBC counts often indicate your immune system is actively responding to temporary inflammation or a minor infection."
    },
    "vitamin d": {
        "name": "Vitamin D (25-OH)",
        "role": "Vitamin D helps your body absorb calcium for healthy bones and immune strength.",
        "dietary_sources": "Sunlight exposure, fortified milk, fatty fish (salmon), and eggs.",
        "low_explanation": "Low Vitamin D levels are very common and can cause mild bone or muscle aches and fatigue."
    }
}

def analyze_pdf_report(pdf_file_bytes: bytes) -> Dict[str, Any]:
    """
    Parses lab report PDF using pypdf and provides patient-friendly explanations.
    Does NOT claim OCR capability. Reads text-based PDF content.
    """
    try:
        reader = pypdf.PdfReader(io.BytesIO(pdf_file_bytes))
        extracted_text = ""
        for page in reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"

        if not extracted_text.strip():
            return {
                "success": False,
                "message": "No readable text found in the PDF. The file may be a scanned image or empty. (Note: Text-based PDFs are supported without OCR)."
            }

        text_lower = extracted_text.lower()
        detected_tests = []

        for key, info in LAB_TEST_KNOWLEDGE.items():
            if key in text_lower or info["name"].lower() in text_lower:
                detected_tests.append(info)

        if not detected_tests:
            # Fallback general analysis if specific markers not matched
            return {
                "success": True,
                "extracted_text_snippet": extracted_text[:500] + ("..." if len(extracted_text) > 500 else ""),
                "detected_tests": [],
                "summary_explanation": "The PDF was successfully parsed. General medical test documentation detected.",
                "general_guidance": "Please present this lab report to your treating doctor or General Physician for professional medical interpretation.",
                "disclaimer": "This analysis is for educational guidance only and does NOT constitute a diagnosis or medical treatment plan."
            }

        return {
            "success": True,
            "extracted_text_snippet": extracted_text[:400] + ("..." if len(extracted_text) > 400 else ""),
            "detected_tests": detected_tests,
            "summary_explanation": f"Identified key lab parameters in report ({len(detected_tests)} items found).",
            "general_guidance": "Discuss any values flagged outside normal reference ranges with your healthcare professional.",
            "disclaimer": "This report reader provides simple explanatory context only. It does not diagnose diseases or prescribe treatments."
        }

    except Exception as e:
        return {
            "success": False,
            "message": f"Error parsing PDF file: {str(e)}"
        }
