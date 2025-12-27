# src/ats.py
from __future__ import annotations
import re
from typing import Dict, List

def ats_checks(resume_text: str) -> Dict[str, List[str]]:
    """
    Lightweight ATS heuristics. Not perfect, but useful signals.
    """
    warnings: List[str] = []
    tips: List[str] = []

    t = resume_text or ""

    # Tables/pipes often indicate columns
    if "|" in t:
        warnings.append("Detected '|' characters which may indicate tables/columns; ATS can struggle with multi-column resumes.")
        tips.append("Prefer a single-column resume; avoid tables.")

    # Too many short lines can indicate column layout
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    short_lines = sum(1 for ln in lines if len(ln) <= 25)
    if lines and (short_lines / len(lines)) > 0.55:
        warnings.append("Many very short lines detected; may indicate multi-column layout or heavy formatting.")
        tips.append("Use standard section headers and longer bullet lines.")

    # Contact info presence
    if not re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", t):
        warnings.append("No email detected.")
        tips.append("Add a professional email near the top.")
    if not re.search(r"\b(\+?\d[\d\-\s\(\)]{8,}\d)\b", t):
        warnings.append("No phone number detected.")
        tips.append("Add a phone number near the top (optional but common in US resumes).")

    # Date formatting (very rough)
    if not re.search(r"\b(20\d{2}|19\d{2})\b", t):
        warnings.append("No years detected (e.g., 2024). Recruiters often expect dates for roles/projects.")
        tips.append("Add dates for roles/projects (Month YYYY – Month YYYY).")

    # Excessive symbols
    if t.count("•") == 0 and t.count("-") < 3:
        tips.append("Consider using bullets for experience/project impact statements.")

    return {"warnings": warnings, "tips": tips}
