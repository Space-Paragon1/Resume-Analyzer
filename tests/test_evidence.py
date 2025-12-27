from src.evidence import find_skill_evidence

def test_find_skill_evidence_finds_lines():
    resume = """
    Skills: Python, Docker
    Experience: Built CI/CD pipelines using GitHub Actions.
    Projects: Deployed an API with Docker.
    """
    ev = find_skill_evidence(resume, ["Python", "Docker", "Kubernetes"], max_hits_per_skill=3)
    assert "Python" in ev or "python" in {k.lower() for k in ev.keys()}
    # docker should have at least one matching line
    docker_key = next((k for k in ev.keys() if k.lower() == "docker"), None)
    assert docker_key is not None
    assert any("docker" in line.lower() for line in ev[docker_key])

def test_find_skill_evidence_respects_max_hits():
    resume = "Docker\nDocker again\nDocker third\nDocker fourth\n"
    ev = find_skill_evidence(resume, ["Docker"], max_hits_per_skill=2)
    k = next(iter(ev.keys()))
    assert len(ev[k]) == 2
