# src/reporting.py
from __future__ import annotations
from dataclasses import asdict
from typing import Any, Dict, List, Tuple

def build_report(
    overall_100: float,
    section_scores: Dict[str, float],
    jd_to_best: List[Tuple[str, str, float]],
    missing_skills: Dict[str, List[str]],
) -> Dict[str, Any]:
    return {
        "overall_match_score": overall_100,
        "section_scores_0_1": section_scores,
        "weakest_jd_items": [
            {"jd_requirement": jd, "closest_resume_bullet": rb, "score_0_1": s}
            for jd, rb, s in jd_to_best[:12]
        ],
        "missing_skills": missing_skills,
    }
