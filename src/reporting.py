# src/reporting.py
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

def build_report(
    overall_100: float,
    section_scores: Dict[str, float],
    jd_to_best: List[Tuple[str, str, float]],
    missing_skills: Dict[str, List[str]],
    suggestions: Optional[List[Dict[str, str]]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    top_n: int = 20,
) -> Dict[str, Any]:
    report: Dict[str, Any] = {
        "overall_match_score": overall_100,
        "section_scores_0_1": {k: round(v, 4) for k, v in section_scores.items()},
        "weakest_jd_items": [
            {"jd_requirement": jd, "closest_resume_bullet": rb, "score_0_1": round(s, 4)}
            for jd, rb, s in jd_to_best[:top_n]
        ],
        "missing_skills": missing_skills,
    }

    if suggestions:
        report["suggestions"] = [
            {
                "score": s.get("score", ""),
                "jd_requirement": s.get("jd_req", ""),
                "closest_bullet": s.get("closest_bullet", ""),
                "suggested_rewrite": s.get("suggestion", ""),
                "evidence_tip": s.get("evidence_tip", ""),
            }
            for s in suggestions
        ]

    report["metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_jd_chunks": len(jd_to_best),
        **(metadata or {}),
    }

    return report
