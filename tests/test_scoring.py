import numpy as np
from src.scoring import compute_section_score, match_jd_to_resume, weighted_overall

def test_weighted_overall_basic():
    scores = {"skills": 0.5, "experience": 1.0, "projects": 0.0}
    overall = weighted_overall(scores)
    assert 0.0 <= overall <= 1.0

def test_compute_section_score_shapes():
    # 2 JD vectors, 3 resume vectors
    jd = np.array([[1, 0], [0, 1]], dtype=np.float32)
    resume = np.array([[1, 0], [1, 0], [0, 1]], dtype=np.float32)
    score = compute_section_score(jd, resume)
    assert 0.0 <= score <= 1.0

def test_match_jd_to_resume_returns_sorted_low_to_high():
    jd_chunks = ["A", "B"]
    resume_chunks = ["r1", "r2"]
    jd_emb = np.array([[1, 0], [0, 1]], dtype=np.float32)
    resume_emb = np.array([[1, 0], [0, 1]], dtype=np.float32)

    out = match_jd_to_resume(jd_chunks, jd_emb, resume_chunks, resume_emb)
    assert len(out) == 2
    # Should be sorted by score ascending
    assert out[0][2] <= out[1][2]
