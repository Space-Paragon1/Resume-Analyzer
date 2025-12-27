from src.reporting import build_report

def test_build_report_structure():
    overall_100 = 72.5
    section_scores = {"skills": 0.7, "experience": 0.8, "projects": 0.6}
    jd_to_best = [("Req A", "Bullet A", 0.5), ("Req B", "Bullet B", 0.2)]
    grouped = {"core": ["python"], "tools": ["docker"], "nice_to_have": []}

    report = build_report(overall_100, section_scores, jd_to_best, grouped)

    assert report["overall_match_score"] == overall_100
    assert "section_scores_0_1" in report
    assert "weakest_jd_items" in report
    assert isinstance(report["weakest_jd_items"], list)
    assert report["missing_skills"] == grouped
