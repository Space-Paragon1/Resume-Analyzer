from src.ats import ats_checks

def test_ats_detects_missing_email_and_phone():
    resume = "John Doe\nSoftware Engineer\n"
    out = ats_checks(resume)
    assert any("email" in w.lower() for w in out["warnings"])
    assert any("phone" in w.lower() for w in out["warnings"])

def test_ats_detects_pipes_as_tables():
    resume = "Name | Email | Phone\nJohn | john@email.com | 123-456-7890\n"
    out = ats_checks(resume)
    assert any("tables" in w.lower() or "columns" in w.lower() for w in out["warnings"])
