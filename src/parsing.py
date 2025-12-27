from __future__ import annotations

import re
from typing import Optional

import fitz  # PyMuPDF


def clean_text(text: str) -> str:
    """Normalize text for analysis:

    - Replace non-breaking spaces with normal spaces
    - Replace tabs with spaces
    - Collapse runs of spaces into a single space (per-line)
    - Collapse 3+ newlines into exactly two newlines
    - Strip whitespace at the edges and strip each line
    """
    if text is None:
        return ""

    # Normalize newlines first
    s = text.replace('\r\n', '\n').replace('\r', '\n')
    # Replace NBSP and tabs
    s = s.replace('\xa0', ' ').replace('\t', ' ')

    # Collapse long runs of newlines to two newlines
    s = re.sub(r"\n{3,}", "\n\n", s)

    # Strip whitespace on each line to remove leading/trailing spaces
    lines = [ln.strip() for ln in s.split('\n')]
    s = '\n'.join(lines)

    # Collapse multiple spaces within lines
    s = re.sub(r" {2,}", " ", s)

    # Final trim
    return s.strip()


def read_text_input(value: Optional[str]) -> str:
    """Safe reader for text inputs: returns cleaned string or empty string for null/blank."""
    if not value:
        return ""
    # If value contains only whitespace/newlines, treat as empty
    if value.strip() == "":
        return ""
    return clean_text(value)


def extract_text_from_pdf(stream: bytes) -> str:
    """Extract text from a PDF byte stream and clean it.

    Uses `fitz.open(stream=..., filetype='pdf')` so tests can monkeypatch `fitz.open`.
    """
    doc = fitz.open(stream=stream, filetype="pdf")
    pages = [page.get_text("text") for page in doc]
    combined = "\n".join(pages)
    return clean_text(combined)
