from src.chunking import bulletize

def test_bulletize_splits_lines():
    text = """
    - Built API in Python
    - Deployed with Docker
    """
    bullets = bulletize(text)
    assert len(bullets) >= 2
    assert any("python" in b.lower() for b in bullets)
