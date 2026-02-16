# src/skills.py
from __future__ import annotations
import re
from typing import List, Set, Dict

DEFAULT_SKILLS = [
    # Core CS / SWE
    "python", "java", "c++", "c#", "go", "rust", "ruby", "scala", "kotlin", "swift",
    "javascript", "typescript", "html", "css", "bash", "shell scripting",
    "sql", "linux", "git", "rest", "api", "graphql", "grpc",
    "microservices", "distributed systems", "systems design", "object-oriented programming",
    "data structures", "algorithms", "concurrency", "multithreading",
    # Web / Backend Frameworks
    "react", "vue", "angular", "next.js", "node.js", "express",
    "fastapi", "flask", "django", "spring boot", "rails",
    # DevOps / Cloud
    "docker", "podman", "kubernetes", "helm", "terraform", "ansible",
    "ci/cd", "github actions", "jenkins", "gitlab ci", "argocd",
    "aws", "gcp", "azure", "openstack",
    "s3", "ec2", "lambda", "cloud functions", "cloud run",
    # Databases
    "postgresql", "mysql", "sqlite", "mongodb", "redis",
    "elasticsearch", "cassandra", "dynamodb", "snowflake", "bigquery",
    # Data / ML / AI
    "pytorch", "tensorflow", "scikit-learn", "numpy", "pandas", "scipy",
    "machine learning", "deep learning", "nlp", "computer vision",
    "transformers", "hugging face", "fine-tuning", "llm", "langchain",
    "llamaindex", "openai", "cuda", "spark", "kafka", "airflow", "dbt",
    "databricks", "mlflow", "feature engineering", "data pipelines",
    # Testing
    "pytest", "jest", "unit testing", "integration testing", "tdd", "selenium",
    # Other
    "agile", "scrum", "jira", "open source",
]

# Sets for categorization
_CORE_SKILLS = {
    "python", "java", "c++", "c#", "go", "javascript", "typescript", "sql",
    "linux", "git", "data structures", "algorithms", "systems design",
    "object-oriented programming", "rest", "api",
}
_TOOLS_SKILLS = {
    "docker", "kubernetes", "helm", "terraform", "ansible", "ci/cd",
    "github actions", "jenkins", "gitlab ci", "aws", "azure", "gcp",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "snowflake", "bigquery", "dynamodb", "kafka", "spark", "airflow",
    "fastapi", "flask", "django", "spring boot", "react", "node.js",
}

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

def extract_skills_dynamic(jd_text: str, known_skills: Set[str] | None = None) -> Set[str]:
    """Extract skill-like tokens from JD text that aren't in the default list.

    Pulls out capitalized acronyms (AWS, CI/CD), CamelCase words (FastAPI, LangChain),
    and version-tagged terms (Python 3, Java 17) that look like tech skills.
    """
    if known_skills is None:
        known_skills = set(s.lower() for s in DEFAULT_SKILLS)

    dynamic: Set[str] = set()

    # Acronyms: 2–6 uppercase letters optionally joined by /
    for m in re.findall(r"\b[A-Z]{2,6}(?:/[A-Z]{2,6})?\b", jd_text):
        candidate = m.strip()
        if len(candidate) >= 2 and candidate.lower() not in known_skills:
            # Filter out common non-skill words
            if candidate not in {"THE", "AND", "OR", "FOR", "WITH", "YOU", "WE",
                                  "ARE", "WILL", "CAN", "NOT", "ALL", "HAS", "IN",
                                  "IS", "IT", "TO", "BE", "OF", "AT", "AN"}:
                dynamic.add(candidate)

    # CamelCase / PascalCase (e.g. LangChain, FastAPI, TensorFlow, GitHub)
    for m in re.findall(r"\b[A-Z][a-z]+(?:[A-Z][a-z]*)+\b", jd_text):
        candidate = m.strip()
        if candidate.lower() not in known_skills:
            dynamic.add(candidate)

    return dynamic

def categorize_missing(missing: Set[str]) -> Dict[str, List[str]]:
    core: List[str] = []
    tools: List[str] = []
    nice: List[str] = []
    for s in sorted(missing):
        if s in _CORE_SKILLS:
            core.append(s)
        elif s in _TOOLS_SKILLS:
            tools.append(s)
        else:
            nice.append(s)
    return {"core": core, "tools": tools, "nice_to_have": nice}
