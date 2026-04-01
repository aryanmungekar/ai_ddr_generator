import os
import json
import fitz
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import google.generativeai as genai


# REPORTLAB
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

app = Flask(__name__)

# =========================
# CONFIG
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "outputs")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

# =========================
# API KEY
# =========================
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found. Set it in environment variables.")

genai.configure(api_key=API_KEY)

# =========================
# FILE NAMING
# =========================
def get_next_filename(base_name, ext):
    files = os.listdir(OUTPUT_FOLDER)
    nums = []

    for f in files:
        if f.startswith(base_name) and f.endswith(f".{ext}"):
            try:
                n = int(f.replace(base_name, "").replace(f".{ext}", ""))
                nums.append(n)
            except:
                pass

    next_num = max(nums) + 1 if nums else 1
    return os.path.join(OUTPUT_FOLDER, f"{base_name}{next_num}.{ext}")

# =========================
# TRACK LATEST FILE
# =========================
def save_latest(json_path):
    with open(os.path.join(OUTPUT_FOLDER, "latest.json"), "w") as f:
        json.dump({"latest_file": json_path}, f)

def get_latest_file():
    path = os.path.join(OUTPUT_FOLDER, "latest.json")
    if not os.path.exists(path):
        return None

    with open(path) as f:
        return json.load(f).get("latest_file")

# =========================
# TEXT EXTRACTION
# =========================
def extract_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "".join([page.get_text() for page in doc])

def clean_text(text):
    lines = text.split("\n")
    cleaned = []

    garbage = ["photo", "image", "serial number", "checklist", "%"]

    for line in lines:
        line = line.strip()
        if len(line) < 3:
            continue
        if any(g in line.lower() for g in garbage):
            continue
        cleaned.append(line)

    return "\n".join(cleaned)

# =========================
# PROMPT
# =========================
def generate_prompt(ins, thr):
    return f"""
You are a Building Diagnostics Expert.

Return ONLY valid JSON.

{{
  "summary": "",
  "observations": [{{"area": "", "issues": []}}],
  "root_cause": "",
  "severity": {{
    "level": "",
    "score": "",
    "reason": ""
  }},
  "recommendations": [],
  "notes": "",
  "missing": {{
    "critical": [],
    "recommended": []
  }}
}}

INSPECTION:
{ins}

THERMAL:
{thr}
"""

# =========================
# SAFE EXTRACT
# =========================
def safe_extract_text(res):
    try:
        return res.text
    except:
        try:
            return res.candidates[0].content.parts[0].text
        except:
            return ""

# =========================
# PDF GENERATION
# =========================
def generate_pdf_from_json(data, pdf_path):

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        name="TitleCustom",
        fontSize=20,
        leading=24,
        spaceAfter=10,
        alignment=1
    )

    section_style = ParagraphStyle(
        name="Section",
        fontSize=14,
        leading=16,
        spaceAfter=8,
        textColor=colors.darkblue
    )

    body_style = styles["BodyText"]

    elements = []

    elements.append(Paragraph("UrbanRoof Diagnostics Pvt. Ltd.", title_style))
    elements.append(Paragraph("Detailed Diagnostic Report (DDR)", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph("1. Summary", section_style))
    elements.append(Paragraph(data.get("summary", "N/A"), body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("2. Severity Assessment", section_style))
    sev = data.get("severity", {})

    severity_text = f"""
    <b>Level:</b> {sev.get('level')}<br/>
    <b>Score:</b> {sev.get('score')}<br/>
    <b>Reason:</b> {sev.get('reason')}
    """

    elements.append(Paragraph(severity_text, body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("3. Root Cause Analysis", section_style))
    elements.append(Paragraph(data.get("root_cause", "N/A"), body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("4. Area-wise Observations", section_style))
    for area in data.get("observations", []):
        elements.append(Paragraph(f"<b>{area.get('area')}</b>", styles["Heading3"]))
        for issue in area.get("issues", []):
            elements.append(Paragraph(f"• {issue}", body_style))
        elements.append(Spacer(1, 8))

    elements.append(Paragraph("5. Recommendations", section_style))
    for rec in data.get("recommendations", []):
        elements.append(Paragraph(f"• {rec}", body_style))

    elements.append(Spacer(1, 10))

    elements.append(Paragraph("6. Notes", section_style))
    elements.append(Paragraph(data.get("notes", "N/A"), body_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("7. Missing Information", section_style))

    missing = data.get("missing", {"critical": [], "recommended": []})
    table_data = [["Type", "Details"]]

    for i in missing.get("critical", []):
        table_data.append(["Critical", i])

    for i in missing.get("recommended", []):
        table_data.append(["Recommended", i])

    table = Table(table_data, colWidths=[100, 350])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.darkblue),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 20))
    elements.append(Paragraph("Generated by UrbanRoof AI System", styles["Italic"]))

    doc.build(elements)

# =========================
# ROUTES
# =========================

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")

    try:
        f1 = request.files.get("inspection")
        f2 = request.files.get("thermal")

        if not f1 or not f2:
            return jsonify({"error": "Upload both files"})

        p1 = os.path.join(UPLOAD_FOLDER, secure_filename(f1.filename))
        p2 = os.path.join(UPLOAD_FOLDER, secure_filename(f2.filename))

        f1.save(p1)
        f2.save(p2)

        text1 = clean_text(extract_text(p1))
        text2 = clean_text(extract_text(p2))

        prompt = generate_prompt(text1[:2000], text2[:1000])

        # ✅ Gemini correct usage
        model = genai.GenerativeModel("gemini-2.5")
        res = model.generate_content(prompt)

        try:
            output_text = safe_extract_text(res)
            data = json.loads(output_text)
        except:
            return jsonify({"error": "Invalid JSON from AI"})

        json_path = get_next_filename("ddr", "json")

        with open(json_path, "w") as f:
            json.dump(data, f, indent=4)

        save_latest(json_path)

        return jsonify({"status": "success"})

    except Exception as e:
        return jsonify({"error": str(e)})

# =========================
# DOWNLOAD PDF
# =========================
@app.route("/download-pdf")
def download_pdf():

    json_path = get_latest_file()

    if not json_path or not os.path.exists(json_path):
        return "No report found"

    pdf_path = json_path.replace(".json", ".pdf")

    # generate only if not exists
    if not os.path.exists(pdf_path):
        with open(json_path) as f:
            data = json.load(f)
        generate_pdf_from_json(data, pdf_path)

    return send_file(pdf_path, as_attachment=True)

# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)