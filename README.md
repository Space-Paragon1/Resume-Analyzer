# Resume–Job Description Analyzer (AI)

An AI-powered Streamlit web application that analyzes how well a resume matches a given job description.  
It uses transformer-based sentence embeddings and practical heuristics to highlight strengths, gaps, and areas for improvement.

---

## Features
- **Overall match score (0–100)** with section breakdown:
  - Skills
  - Experience
  - Projects
- **Weakest-covered job requirements** with closest matching resume bullets
- **Suggested bullet rewrites** using metric-driven templates
- **Missing skills detection** based on keyword analysis
- **Skill evidence viewer** showing exact resume lines where skills appear
- **Basic ATS checks** to flag common formatting issues
- **Exportable JSON report** summarizing the analysis

---

## Tech Stack
- **Python**
- **Streamlit** – user interface
- **sentence-transformers** – semantic embeddings
- **PyMuPDF** – PDF text extraction

---

## Project Structure
resume-jd-analyzer/
├── app/
│ └── app.py # Streamlit entry point
├── src/
│ ├── init.py
│ ├── parsing.py
│ ├── chunking.py
│ ├── embeddings.py
│ ├── scoring.py
│ ├── skills.py
│ ├── suggestions.py
│ ├── evidence.py
│ ├── ats.py
│ └── reporting.py
├── requirements.txt
├── README.md
└── .gitignore


---

## Setup (Local)

### 1. Create and activate a virtual environment (recommended)

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1

**macOS/ Linux**
python3 -m venv .venv
source .venv/bin/activate

2. Install dependencies
pip install -r requirements.txt

3. Run the app
streamlit run app/app.py

Usage
1) Paste or upload your resume (PDF optional)
2) Paste a job description
3) Click Analyze
4) Review:
   - Match scores
   - Weakest job requirements
   - Suggested resume bullet rewrites
   - Missing skills and skill evidence
   - ATS feedback
5) Download the JSON report via the Export report button

   Deployment
   - This app is designed to be deployed on Streamlit Community Cloud.
   - Main file path: app/app.py
   - Ensure src/__init__.py exists to avoid import errors

   Notes & Limitations
   - Skill detection is keyword-based and depends on the built-in skill list
   - PDF text extraction quality depends on resume formatting
   - Suggested bullet rewrites are templates and should be edited with truthful metrics

   Future Improvements
   - Rank resume against multiple job descriptions
   - Custom skill dictionary upload
   - PDF report export
   - Improved resume section detection