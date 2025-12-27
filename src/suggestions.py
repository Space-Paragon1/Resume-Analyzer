# src/suggestions.py
from __future__ import annotations
import re
from typing import List, Tuple, Dict

ACTION_VERBS = [
    "Built", "Developed", "Implemented", "Designed", "Optimized",
    "Automated", "Deployed", "Improved", "Accelerated", "Reduced",
    "Refactored", "Integrated", "Led", "Collaborated", "Analyzed",
]

METRIC_HINTS = [
    "runtime by X%", "latency by Xms", "cost by $X", "errors by X%",
    "throughput to X req/s", "accuracy to X%", "manual effort by X hrs/week",
]

def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())

def detect_skill_terms(text: str) -> List[str]:
    """
    Lightweight extractor: returns capitalized terms/acronyms and common tech tokens.
    """
    text = text or ""
    tokens = set()

    # acronyms / tools (e.g., CI/CD, GPU, API)
    for m in re.findall(r"\b[A-Z]{2,}(?:/[A-Z]{2,})?\b", text):
        tokens.add(m)

    # common tech words (simple heuristic)
    for m in re.findall(r"\b(?:python|java|c\+\+|sql|docker|kubernetes|pytorch|tensorflow|linux|git|api|cloud|aws|azure|gcp|openstack|distributed|pipeline|ci/cd|testing|unit tests)\b", text.lower()):
        tokens.add(m.lower())

    return sorted(tokens)

def propose_bullet(jd_req: str, closest_bullet: str) -> Dict[str, str]:
    """
    Produce a rewrite template grounded in the closest resume bullet + JD requirement.
    """
    jd_req = _clean(jd_req)
    closest_bullet = _clean(closest_bullet)

    jd_terms = detect_skill_terms(jd_req)
    rb_terms = detect_skill_terms(closest_bullet)
    important = ", ".join(jd_terms[:6]) if jd_terms else "key skills"

    verb = ACTION_VERBS[0]
    metric = METRIC_HINTS[0]

    # If closest bullet exists, keep its "topic" but upgrade structure + metrics
    if closest_bullet:
        base = closest_bullet
        # remove trailing period to avoid double punctuation
        base = base[:-1] if base.endswith(".") else base
        suggestion = (
            f"{verb} {base} to align with {important}, improving {metric} "
            f"(add a real metric)."
        )
    else:
        suggestion = (
            f"{verb} a project aligned to: {jd_req} using {important}; "
            f"improved {metric} (add a real metric)."
        )

    evidence = "Add evidence: dataset size/users, stack/tools, and a measurable result."
    terms = f"JD terms: {', '.join(jd_terms) if jd_terms else 'N/A'} | Resume terms: {', '.join(rb_terms) if rb_terms else 'N/A'}"

    return {
        "suggestion": suggestion,
        "evidence_tip": evidence,
        "terms_debug": terms,
    }

def generate_suggestions(jd_to_best: List[Tuple[str, str, float]], n: int = 6) -> List[Dict[str, str]]:
    """
    Take jd_to_best list (sorted low->high) and return n suggestion objects.
    """
    out = []
    for jd_req, best_bullet, score in jd_to_best[:n]:
        pkg = propose_bullet(jd_req, best_bullet)
        pkg["score"] = f"{score*100:.1f}/100"
        pkg["jd_req"] = jd_req
        pkg["closest_bullet"] = best_bullet
        out.append(pkg)
    return out
