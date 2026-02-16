# src/ats.py
from __future__ import annotations
import re
from typing import Dict, List

_ACTION_VERBS = {
    "built", "developed", "implemented", "designed", "optimized", "automated",
    "deployed", "improved", "accelerated", "reduced", "refactored", "integrated",
    "led", "collaborated", "analyzed", "created", "managed", "delivered",
    "launched", "engineered", "architected", "streamlined", "increased",
    "decreased", "migrated", "scaled", "maintained", "reviewed", "mentored",
}

def ats_checks(resume_text: str) -> Dict[str, List[str]]:
    """
    ATS heuristics covering formatting, content, and style issues.
    Returns {'warnings': [...], 'tips': [...], 'positives': [...]}.
    """
    warnings: List[str] = []
    tips: List[str] = []
    positives: List[str] = []

    t = resume_text or ""
    lines = [ln.strip() for ln in t.splitlines() if ln.strip()]
    words = t.split()

    # ── Formatting ────────────────────────────────────────────────────────────

    # Tables/pipes often indicate columns
    if "|" in t:
        warnings.append("Detected '|' characters — may indicate tables/columns. ATS parsers often struggle with multi-column resumes.")
        tips.append("Use a single-column layout and avoid tables.")

    # Too many short lines → multi-column layout
    short_lines = sum(1 for ln in lines if len(ln) <= 25)
    if lines and (short_lines / len(lines)) > 0.55:
        warnings.append("Many very short lines detected — may indicate a multi-column or heavily formatted layout.")
        tips.append("Use standard section headers and longer, full-sentence bullet lines.")

    # Lines that are suspiciously long (>120 chars can wrap oddly)
    long_lines = [ln for ln in lines if len(ln) > 120]
    if len(long_lines) > 3:
        warnings.append(f"{len(long_lines)} lines exceed 120 characters — may cause wrapping or parsing issues.")
        tips.append("Keep bullet points under ~120 characters for clean formatting.")

    # Unicode special characters that confuse ATS
    curly_quotes = re.findall(r'[""'']', t)
    em_dashes = re.findall(r'[—–]', t)
    if curly_quotes:
        warnings.append(f"Found {len(curly_quotes)} curly/smart quote(s) (\u201c\u201d\u2018\u2019). Some ATS systems misread these.")
        tips.append("Replace curly quotes with straight quotes (\").")
    if em_dashes:
        warnings.append(f"Found {len(em_dashes)} em/en dash(es) (— or –). Some ATS parsers can't handle them.")
        tips.append("Replace em-dashes with hyphens (-).")

    # Overuse of ALL-CAPS text
    all_caps_words = [w for w in words if w.isupper() and len(w) > 2 and w.isalpha()]
    if words and (len(all_caps_words) / len(words)) > 0.15:
        warnings.append(f"{len(all_caps_words)} ALL-CAPS words found ({len(all_caps_words)/len(words)*100:.0f}% of total). Excessive caps can confuse parsers.")
        tips.append("Use title case for section headers instead of ALL-CAPS.")

    # ── Content ───────────────────────────────────────────────────────────────

    # Contact info: email
    if re.search(r"\b[\w\.-]+@[\w\.-]+\.\w+\b", t):
        positives.append("Email address detected.")
    else:
        warnings.append("No email address detected.")
        tips.append("Add a professional email near the top of your resume.")

    # Contact info: phone
    if re.search(r"\b(\+?\d[\d\-\s\(\)]{8,}\d)\b", t):
        positives.append("Phone number detected.")
    else:
        warnings.append("No phone number detected.")
        tips.append("Add a phone number (optional but expected in many regions).")

    # LinkedIn / GitHub presence
    if re.search(r"linkedin\.com/in/", t, re.IGNORECASE):
        positives.append("LinkedIn profile URL detected.")
    else:
        tips.append("Consider adding your LinkedIn profile URL.")
    if re.search(r"github\.com/", t, re.IGNORECASE):
        positives.append("GitHub profile URL detected.")

    # Dates for roles
    if re.search(r"\b(20\d{2}|19\d{2})\b", t):
        positives.append("Year dates detected — good for ATS chronological parsing.")
    else:
        warnings.append("No years detected (e.g., 2024). Recruiters expect dates on roles/projects.")
        tips.append("Add dates for all roles and projects (Month YYYY – Month YYYY).")

    # Key section headers present
    has_experience = bool(re.search(r"\bexperience\b", t, re.IGNORECASE))
    has_skills = bool(re.search(r"\bskills\b", t, re.IGNORECASE))
    has_education = bool(re.search(r"\beducation\b", t, re.IGNORECASE))
    if not has_experience:
        warnings.append("No 'Experience' section header detected.")
        tips.append("Add an 'Experience' or 'Work Experience' section header.")
    if not has_skills:
        tips.append("Consider adding a 'Skills' section for easy keyword scanning.")
    if not has_education:
        tips.append("Consider adding an 'Education' section.")

    # ── Style ─────────────────────────────────────────────────────────────────

    # Bullets present
    bullet_count = t.count("•") + t.count("·") + len(re.findall(r"^\s*[-*]\s", t, re.MULTILINE))
    if bullet_count >= 5:
        positives.append(f"Bullet points detected ({bullet_count}) — good for readability and ATS parsing.")
    elif t.count("•") == 0 and t.count("-") < 3:
        tips.append("Use bullet points for experience/project impact statements.")

    # Action verbs
    first_words = set()
    for ln in lines:
        parts = ln.split()
        if parts:
            first_words.add(parts[0].lower().rstrip(".,:;"))
    used_verbs = first_words & _ACTION_VERBS
    if len(used_verbs) >= 3:
        positives.append(f"Strong action verbs detected: {', '.join(sorted(used_verbs)[:5])}.")
    else:
        tips.append("Start bullet points with strong action verbs (e.g., Built, Optimized, Led, Deployed).")

    # Resume length
    word_count = len(words)
    if word_count < 200:
        warnings.append(f"Resume appears very short ({word_count} words). Most ATS expect at least 300 words.")
        tips.append("Expand your resume with more detail on projects and experience.")
    elif word_count > 1200:
        tips.append(f"Resume is long ({word_count} words). Consider trimming to 1–2 pages for readability.")
    else:
        positives.append(f"Resume length looks good ({word_count} words).")

    return {"warnings": warnings, "tips": tips, "positives": positives}
