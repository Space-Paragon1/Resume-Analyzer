# src/chunking.py
from __future__ import annotations
import re
from typing import Dict, List

# Canonical section keywords — matching is done by CONTAINS, so variants like
# "Professional Experience" or "WORK EXPERIENCE" will all resolve correctly.
_SECTION_KEYWORDS = [
    "experience",
    "projects",
    "skills",
    "education",
    "certifications",
    "leadership",
    "activities",
    "publications",
    "awards",
    "volunteer",
    "summary",
    "objective",
    "profile",
    "achievements",
]

# Map keyword → canonical name used as dict key
_KEYWORD_TO_CANONICAL: Dict[str, str] = {
    "experience": "experience",
    "projects": "projects",
    "skills": "skills",
    "education": "education",
    "certifications": "certifications",
    "leadership": "leadership",
    "activities": "activities",
    "publications": "publications",
    "awards": "awards",
    "volunteer": "volunteer",
    "summary": "summary",
    "objective": "summary",
    "profile": "summary",
    "achievements": "achievements",
}

def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().lower())

def _strip_decoration(line: str) -> str:
    """Remove leading bullets, hashes, underscores, pipes common in resume headers."""
    return re.sub(r"^[\s#\-\*•|_=]+", "", line).strip()

def _detect_header(line: str) -> str | None:
    """Return canonical section name if line looks like a resume section header, else None."""
    cleaned = _strip_decoration(line)
    normalized = _normalize(cleaned)

    # Must be short (headers are rarely >60 chars) and not look like a bullet
    if len(normalized) > 60:
        return None

    for keyword in _SECTION_KEYWORDS:
        # CONTAINS check: "professional experience" → contains "experience"
        if keyword in normalized:
            return _KEYWORD_TO_CANONICAL[keyword]

    return None

def split_into_sections(resume_text: str) -> Dict[str, str]:
    """
    Fuzzy section splitter: handles varied header styles including
    ALL-CAPS, decorated (## / -- / •), and multi-word variants.
    Falls back to 'full' key if no headers are found.
    """
    lines = [ln.strip() for ln in resume_text.splitlines()]
    header_positions: List[tuple[int, str]] = []

    for i, ln in enumerate(lines):
        canonical = _detect_header(ln)
        if canonical is not None:
            # Avoid treating a line as a header if it has a lot of content
            # (real headers are short; experience bullets may contain "experience")
            word_count = len(ln.split())
            if word_count <= 6:
                header_positions.append((i, canonical))

    if not header_positions:
        return {"full": resume_text.strip()}

    sections: Dict[str, str] = {}
    for idx, (start_i, header) in enumerate(header_positions):
        end_i = header_positions[idx + 1][0] if idx + 1 < len(header_positions) else len(lines)
        body = "\n".join(lines[start_i + 1:end_i]).strip()
        # If same canonical key appears twice, append rather than overwrite
        if header in sections:
            sections[header] = sections[header] + "\n" + body
        else:
            sections[header] = body
    return sections

def bulletize(text: str) -> List[str]:
    """
    Split into bullet-like chunks. Works for '-' '•' '*' and also sentences.
    """
    text = text.strip()
    if not text:
        return []

    # Split on common bullet markers
    chunks = re.split(r"(?:\n\s*[•\-\*]\s+)", "\n" + text)
    chunks = [c.strip() for c in chunks if c.strip()]

    # If no bullets found, split into sentences as fallback
    if len(chunks) <= 1:
        chunks = re.split(r"(?<=[.!?])\s+", text)
        chunks = [c.strip() for c in chunks if len(c.strip()) > 20]

    return chunks

def chunk_job_description(jd_text: str) -> List[str]:
    """
    Break JD into requirement/responsibility-like chunks.
    """
    lines = [ln.strip() for ln in jd_text.splitlines() if ln.strip()]
    # Merge short lines with the previous one to reduce fragmentation
    merged: List[str] = []
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

    chunks: List[str] = []
    for m in merged:
        chunks.extend(bulletize(m))
    return [c for c in chunks if len(c) >= 25]
