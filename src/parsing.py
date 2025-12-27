# src/parsing.py
from __future__ import annotations
import re
from typing import Optional
import fitz  # PyMuPDF

def clean_text(text: str) -> str:
    text = text.replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    parts = []
    for page in doc:
        parts.append(page.get_text("text"))
    return clean_text("\n".join(parts))

def read_text_input(text: Optional[str]) -> str:
    return clean_text(text or "")
