# src/evidence.py
from __future__ import annotations
import re
from typing import Dict, List

def _lines(text: str) -> List[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]

def find_skill_evidence(text: str, skills: List[str], max_hits_per_skill: int = 3) -> Dict[str, List[str]]:
    """
    Returns {skill: [matching_lines...]} using case-insensitive whole-word-ish matching.
    """
    lines = _lines(text)
    evidence: Dict[str, List[str]] = {}
    for skill in skills:
        pat = re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE)
        hits = []
        for ln in lines:
            if pat.search(ln):
                hits.append(ln)
                if len(hits) >= max_hits_per_skill:
                    break
        if hits:
            evidence[skill] = hits
    return evidence
