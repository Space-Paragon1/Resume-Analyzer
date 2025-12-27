# src/skills.py
from __future__ import annotations
import re
from typing import List, Set, Dict

DEFAULT_SKILLS = [
    # Core CS / SWE
    "python","java","c++","javascript","typescript","sql","linux","git",
    "docker","podman","kubernetes","ci/cd","github actions",
    "rest","api","microservices","distributed systems","systems design",
    # Data/ML
    "pytorch","tensorflow","scikit-learn","numpy","pandas",
    "machine learning","deep learning","nlp","computer vision",
    "transformers","hugging face","fine-tuning",
    # Cloud
    "aws","gcp","azure","openstack",
    # Databases
    "postgresql","mysql","mongodb","redis",
]

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())

def extract_skills(text: str, skills_list: List[str] = DEFAULT_SKILLS) -> Set[str]:
    t = normalize(text)
    found = set()
    for s in skills_list:
        pattern = r"\b" + re.escape(s.lower()) + r"\b"
        if re.search(pattern, t):
            found.add(s)
    return found

def categorize_missing(missing: Set[str]) -> Dict[str, List[str]]:
    core = []
    tools = []
    nice = []
    for s in sorted(missing):
        if s in {"python","sql","git","linux","data structures","algorithms","systems design"}:
            core.append(s)
        elif s in {"docker","kubernetes","ci/cd","github actions","aws","azure","gcp","openstack","postgresql","mysql","mongodb","redis"}:
            tools.append(s)
        else:
            nice.append(s)
    return {"core": core, "tools": tools, "nice_to_have": nice}
