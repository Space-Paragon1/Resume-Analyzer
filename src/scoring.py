# src/scoring.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple
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

def weighted_overall(section_scores: Dict[str, float]) -> float:
    # Weights you can tweak
    weights = {
        "skills": 0.40,
        "experience": 0.40,
        "projects": 0.20
    }
    # If sections missing, redistribute to what exists
    present = {k: v for k, v in weights.items() if k in section_scores}
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
