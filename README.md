# 🏗️ DDR Report Generation System (Applied AI Builder)

## 📌 Overview

This project is an AI-powered system that converts **raw inspection reports** and **thermal reports** into a structured, client-friendly **Detailed Diagnostic Report (DDR)**.

The goal is to transform unstructured technical data into a clear, readable, and actionable report using AI.

---

## 🚀 Features

* ✅ Extracts data from inspection & thermal reports
* ✅ Combines multiple data sources logically
* ✅ Removes duplicate observations
* ✅ Handles missing information (`Not Available`)
* ✅ Detects conflicting inputs
* ✅ Generates structured DDR output
* ✅ Supports JSON, HTML, and PDF output formats
* ✅ Integrates relevant images into report (if available)

---

## 🧠 System Workflow

```
Input Documents (Inspection + Thermal)
            ↓
      Data Extraction
            ↓
   Data Cleaning & Merging
            ↓
      AI Processing (LLM)
            ↓
     Structured DDR Output
            ↓
 JSON / HTML / PDF Report
```

---

## ⚙️ Tech Stack

* **Python** – Core backend logic
* **Gemini API** – AI report generation
* **ReportLab** – PDF generation
* **HTML/CSS** – Report visualization
* **JSON** – Structured data handling

---

## 📂 Project Structure

```
project/
│
├── input/                  # Input reports
├── output/                 # Generated DDR reports
├── app.py                  # Main processing script
├── report_generator.py     # DDR generation logic
├── templates/              # HTML templates
├── static/                 # CSS / assets
└── README.md
```

---

## ▶️ How to Run

### 1. Clone the repository

```
git clone https://github.com/your-username/ddr-generator.git
cd ddr-generator
```

### 2. Install dependencies

```
pip install -r requirements.txt
```

### 3. Run the project

```
python app.py
```

### 4. Provide input files

* Upload inspection report
* Upload thermal report

### 5. Generate DDR

* Output will be generated in:

  * JSON
  * HTML
  * PDF

---

## 📊 Output Format (DDR Structure)

The generated report includes:

1. Property Issue Summary
2. Area-wise Observations
3. Probable Root Cause
4. Severity Assessment (with reasoning)
5. Recommended Actions
6. Additional Notes
7. Missing / Unclear Information

---

## ⚠️ Limitations

* Depends on quality of input documents
* Image extraction may not always align perfectly
* AI may miss edge-case conflicts
* API rate limits (Gemini free tier)

---

## 🔮 Future Improvements

* Add validation layer for AI output
* Use embeddings for better data merging
* Improve image-to-text mapping
* Build full UI dashboard for editing reports
* Add support for multiple report formats
* Integrate RAG for higher accuracy

---

## 🎥 Demo

👉 Loom Video: [Add your Loom link here]

---

## 📁 Sample Outputs

* JSON Report
* HTML Report
* PDF Report

(Available in `/output` folder)

---

## 👨‍💻 Author

**Aryan Mungekar**

---

## 📌 Note

This system is designed to work on **similar inspection datasets**, not just the provided sample, ensuring scalability and real-world usability.
