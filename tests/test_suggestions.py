from src.suggestions import generate_suggestions

def test_generate_suggestions_returns_items():
    jd_to_best = [
        ("Need Python", "Built tools in Python for data pipelines", 0.2),
        ("Need Docker", "Containerized apps using Docker", 0.4),
        ("Need Kubernetes", "", 0.1),
    ]
    out = generate_suggestions(jd_to_best, n=2)
    assert len(out) == 2
    assert "suggestion" in out[0]
    assert "jd_req" in out[0]
    assert "score" in out[0]
