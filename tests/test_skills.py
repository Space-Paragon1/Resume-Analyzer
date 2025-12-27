from src.skills import extract_skills, categorize_missing

def test_extract_skills_basic():
    text = "Experienced with Python, Docker, Kubernetes, and AWS. Built CI/CD pipelines."
    skills = extract_skills(text)
    assert "python" in skills
    assert "docker" in skills

def test_extract_skills_case_insensitive():
    text = "PYTHON and pYtOrCh"
    skills = extract_skills(text)
    assert "python" in skills

def test_categorize_missing_groups():
    missing = {"python", "docker", "kubernetes", "leadership", "communication"}
    grouped = categorize_missing(missing)
    assert "core" in grouped and "tools" in grouped and "nice_to_have" in grouped
    # At least one bucket should have content
    assert any(len(v) > 0 for v in grouped.values())
