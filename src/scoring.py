# src/scoring.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class MatchResult:
    overall_score: float
    section_scores: Dict[str, float]
    jd_to_best_resume: List[Tuple[str, str, float]]  # (jd_chunk, best_resume_chunk, score)

def _score_matrix(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if a.size == 0 or b.size == 0:
        return np.zeros((a.shape[0], b.shape[0]))
    return cosine_similarity(a, b)

def weighted_overall(
    section_scores: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
) -> float:
    """Compute weighted overall score.

    weights should sum to 1.0. If None, uses defaults: skills=0.40, exp=0.40, proj=0.20.
    Missing sections are redistributed proportionally among present ones.
    """
    if weights is None:
        weights = {
            "skills": 0.40,
            "experience": 0.40,
            "projects": 0.20,
        }
    # Keep only sections that actually exist in section_scores
    present = {k: weights[k] for k in weights if k in section_scores}
    if not present:
        return float(np.mean(list(section_scores.values()))) if section_scores else 0.0

    wsum = sum(present.values())
    return sum(section_scores[k] * (present[k] / wsum) for k in present)

def compute_section_score(jd_emb: np.ndarray, resume_emb: np.ndarray) -> float:
    sim = _score_matrix(jd_emb, resume_emb)
    # For each JD chunk, take best matching resume chunk, then average
    if sim.size == 0:
        return 0.0
    best = sim.max(axis=1)
    return float(best.mean())

def match_jd_to_resume(jd_chunks: List[str], jd_emb: np.ndarray,
                       resume_chunks: List[str], resume_emb: np.ndarray) -> List[Tuple[str, str, float]]:
    sim = _score_matrix(jd_emb, resume_emb)
    out = []
    for i, jd in enumerate(jd_chunks):
        if sim.shape[1] == 0:
            out.append((jd, "", 0.0))
            continue
        j = int(sim[i].argmax())
        out.append((jd, resume_chunks[j], float(sim[i, j])))
    # Sort by highest mismatch (lowest score) first to show gaps
    out.sort(key=lambda x: x[2])
    return out
