# src/chunking.py
from __future__ import annotations
import re
from typing import Dict, List

RESUME_SECTION_HEADERS = [
    "experience", "work experience",
    "projects", "project experience",
    "skills", "technical skills",
    "education", "certifications", "leadership", "activities"
]

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def split_into_sections(resume_text: str) -> Dict[str, str]:
    """
    Heuristic section splitter: finds common headers and splits resume text.
    Falls back to 'full' if headers aren't found.
    """
    text = resume_text
    lines = [ln.strip() for ln in text.splitlines()]
    # Track where headers appear
    header_positions = []
    for i, ln in enumerate(lines):
        n = _normalize(ln)
        if n in RESUME_SECTION_HEADERS:
            header_positions.append((i, n))

    if not header_positions:
        return {"full": resume_text.strip()}

    sections: Dict[str, str] = {}
    for idx, (start_i, header) in enumerate(header_positions):
        end_i = header_positions[idx + 1][0] if idx + 1 < len(header_positions) else len(lines)
        body = "\n".join(lines[start_i + 1:end_i]).strip()
        sections[header] = body
    return sections

def bulletize(text: str) -> List[str]:
    """
    Split into bullet-like chunks. Works for '-' '•' '*' and also sentences if needed.
    """
    text = text.strip()
    if not text:
        return []

    # Split on common bullet markers
    chunks = re.split(r"(?:\n\s*[•\-\*]\s+)", "\n" + text)
    chunks = [c.strip() for c in chunks if c.strip()]

    # If it looks like no bullets were found, split into sentences as fallback
    if len(chunks) <= 2:
        chunks = re.split(r"(?<=[.!?])\s+", text)
        chunks = [c.strip() for c in chunks if len(c.strip()) > 20]

    return chunks

def chunk_job_description(jd_text: str) -> List[str]:
    """
    Break JD into requirement/responsibility-like chunks.
    """
    # Split on newlines & bullets, keep meaningful lines
    lines = [ln.strip() for ln in jd_text.splitlines() if ln.strip()]
    # Merge short lines with next line to reduce fragmentation
    merged = []
    buffer = ""
    for ln in lines:
        if len(ln) < 35 and buffer:
            buffer += " " + ln
        else:
            if buffer:
                merged.append(buffer)
            buffer = ln
    if buffer:
        merged.append(buffer)

    # Bulletize merged paragraphs too
    chunks = []
    for m in merged:
        chunks.extend(bulletize(m))
    # Final cleanup: remove tiny chunks
    return [c for c in chunks if len(c) >= 25]
