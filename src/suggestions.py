# src/suggestions.py
from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple

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
    """Lightweight extractor: returns capitalized terms/acronyms and common tech tokens."""
    text = text or ""
    tokens: set[str] = set()

    for m in re.findall(r"\b[A-Z]{2,}(?:/[A-Z]{2,})?\b", text):
        tokens.add(m)

    for m in re.findall(
        r"\b(?:python|java|c\+\+|sql|docker|kubernetes|pytorch|tensorflow|linux|git|"
        r"api|cloud|aws|azure|gcp|openstack|distributed|pipeline|ci/cd|testing|unit tests|"
        r"react|node\.js|fastapi|flask|django|spark|kafka|airflow|langchain|llm)\b",
        text.lower(),
    ):
        tokens.add(m.lower())

    return sorted(tokens)

def propose_bullet(jd_req: str, closest_bullet: str) -> Dict[str, str]:
    """Produce a rewrite template grounded in the closest resume bullet + JD requirement."""
    jd_req = _clean(jd_req)
    closest_bullet = _clean(closest_bullet)

    jd_terms = detect_skill_terms(jd_req)
    rb_terms = detect_skill_terms(closest_bullet)
    important = ", ".join(jd_terms[:6]) if jd_terms else "key skills"

    verb = ACTION_VERBS[0]
    metric = METRIC_HINTS[0]

    if closest_bullet:
        base = closest_bullet[:-1] if closest_bullet.endswith(".") else closest_bullet
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
    """Template-based suggestions (fallback when no API key is provided)."""
    out = []
    for jd_req, best_bullet, score in jd_to_best[:n]:
        pkg = propose_bullet(jd_req, best_bullet)
        pkg["score"] = f"{score*100:.1f}/100"
        pkg["jd_req"] = jd_req
        pkg["closest_bullet"] = best_bullet
        out.append(pkg)
    return out

def generate_ai_suggestions(
    jd_to_best: List[Tuple[str, str, float]],
    api_key: str,
    n: int = 6,
    model: str = "claude-haiku-4-5-20251001",
) -> List[Dict[str, str]]:
    """AI-powered suggestions using Claude API.

    Falls back to template-based suggestions if the API call fails.
    Requires `anthropic` package to be installed.
    """
    try:
        import anthropic
    except ImportError:
        return generate_suggestions(jd_to_best, n=n)

    client = anthropic.Anthropic(api_key=api_key)
    out = []

    for jd_req, best_bullet, score in jd_to_best[:n]:
        jd_req_c = _clean(jd_req)
        best_bullet_c = _clean(best_bullet)

        prompt = (
            "You are an expert resume coach. Rewrite the resume bullet below so it "
            "directly addresses the job requirement. The rewrite must:\n"
            "- Start with a strong action verb\n"
            "- Include a quantifiable metric placeholder like [X%], [$X], or [X users]\n"
            "- Be one sentence, under 120 characters\n"
            "- Incorporate relevant keywords from the job requirement\n\n"
            f"Job requirement: {jd_req_c}\n\n"
            f"Current resume bullet: {best_bullet_c if best_bullet_c else '(none — write a new bullet)'}\n\n"
            "Respond with ONLY the rewritten bullet. No explanation, no quotes."
        )

        try:
            response = client.messages.create(
                model=model,
                max_tokens=150,
                messages=[{"role": "user", "content": prompt}],
            )
            ai_bullet = response.content[0].text.strip()
        except Exception:
            # Fall back to template for this item
            ai_bullet = propose_bullet(jd_req_c, best_bullet_c)["suggestion"]

        jd_terms = detect_skill_terms(jd_req_c)
        rb_terms = detect_skill_terms(best_bullet_c)

        out.append({
            "suggestion": ai_bullet,
            "evidence_tip": "Fill in the metric placeholder with a real number from your experience.",
            "terms_debug": f"JD terms: {', '.join(jd_terms) or 'N/A'} | Resume terms: {', '.join(rb_terms) or 'N/A'}",
            "score": f"{score*100:.1f}/100",
            "jd_req": jd_req_c,
            "closest_bullet": best_bullet_c,
        })

    return out
