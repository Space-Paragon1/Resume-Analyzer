# app/app.py
from __future__ import annotations
import streamlit as st

from src.evidence import find_skill_evidence
from src.ats import ats_checks
from src.skills import extract_skills, categorize_missing
from src.suggestions import generate_suggestions
from src.reporting import build_report
import json
from src.parsing import extract_text_from_pdf, read_text_input
from src.chunking import split_into_sections, bulletize, chunk_job_description
from src.embeddings import Embedder
from src.scoring import compute_section_score, weighted_overall, match_jd_to_resume

st.set_page_config(page_title="Resume–JD Analyzer", layout="wide")

st.title("Resume–Job Description Analyzer (AI)")
st.caption("Upload or paste a resume and job description. Get match score, best-aligned bullets, and missing skills.")

# Sidebar options
with st.sidebar:
    st.header("Settings")
    model_name = st.text_input("Embedding model", value="all-MiniLM-L6-v2")
    show_debug = st.checkbox("Show debug chunks", value=False)
    st.markdown("---")
    st.write("Tip: Start with pasted text for speed. Add PDF later.")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Resume")
    resume_pdf = st.file_uploader("Upload Resume (PDF optional)", type=["pdf"])
    resume_text = st.text_area("Or paste resume text", height=260)

with col2:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste job description", height=350)

analyze = st.button("Analyze", type="primary")

if analyze:
    # Parse resume
    if resume_pdf is not None:
        resume_raw = extract_text_from_pdf(resume_pdf.read())
    else:
        resume_raw = read_text_input(resume_text)

    jd_raw = read_text_input(jd_text)

    if len(resume_raw) < 200 or len(jd_raw) < 200:
        st.error("Please provide more complete resume and job description text (at least ~200 characters each).")
        st.stop()

    # Chunking
    sections = split_into_sections(resume_raw)
    jd_chunks = chunk_job_description(jd_raw)

    # Pick chunks for main sections (heuristic mapping)
    skills_text = sections.get("skills", "") or sections.get("technical skills", "")
    exp_text = sections.get("experience", "") or sections.get("work experience", "")
    proj_text = sections.get("projects", "") or sections.get("project experience", "")

    skills_chunks = bulletize(skills_text) if skills_text else []
    exp_chunks = bulletize(exp_text) if exp_text else []
    proj_chunks = bulletize(proj_text) if proj_text else []

    # If section chunks missing, fall back to full resume bullets
    full_chunks = bulletize(sections.get("full", resume_raw))

    if not skills_chunks:
        skills_chunks = full_chunks
    if not exp_chunks:
        exp_chunks = full_chunks
    if not proj_chunks:
        proj_chunks = full_chunks

    # Embeddings
    embedder = Embedder(model_name)
    jd_emb = embedder.embed(jd_chunks)

    skills_emb = embedder.embed(skills_chunks)
    exp_emb = embedder.embed(exp_chunks)
    proj_emb = embedder.embed(proj_chunks)

    # Scores
    section_scores = {
        "skills": compute_section_score(jd_emb, skills_emb),
        "experience": compute_section_score(jd_emb, exp_emb),
        "projects": compute_section_score(jd_emb, proj_emb),
    }
    overall = weighted_overall(section_scores)

    # Scale to 0-100
    overall_100 = round(overall * 100, 1)

    st.markdown("## Results")
    top = st.columns(4)
    top[0].metric("Overall Match", f"{overall_100}/100")
    top[1].metric("Skills Score", f"{section_scores['skills']*100:.1f}/100")
    top[2].metric("Experience Score", f"{section_scores['experience']*100:.1f}/100")
    top[3].metric("Projects Score", f"{section_scores['projects']*100:.1f}/100")

    # Best matches (use full resume chunks for matching view)
    resume_chunks_for_match = full_chunks
    resume_emb_for_match = embedder.embed(resume_chunks_for_match)
    jd_to_best = match_jd_to_resume(jd_chunks, jd_emb, resume_chunks_for_match, resume_emb_for_match)

    st.markdown("### Weakest-covered JD requirements (fix these first)")
    # Show the 8 lowest matches
    for jd_req, best_bullet, score in jd_to_best[:8]:
        with st.expander(f"Score {score*100:.1f}/100 — {jd_req[:90]}{'...' if len(jd_req)>90 else ''}"):
            st.write("**JD requirement:**")
            st.write(jd_req)
            st.write("**Closest resume bullet:**")
            st.write(best_bullet if best_bullet else "_No match found_")
    

    st.markdown("### Suggested bullet rewrites (fill in real metrics)")
    suggestions = generate_suggestions(jd_to_best, n=6)

    for s in suggestions:
        with st.expander(f"Score {s['score']} — Suggested rewrite"):
            st.write("**JD requirement:**")
            st.write(s["jd_req"])
            st.write("**Closest resume bullet:**")
            st.write(s["closest_bullet"] if s["closest_bullet"] else "_No match found_")
            st.write("**Suggested bullet (template):**")
            st.write(s["suggestion"])
            st.write("**Evidence tip:**")
            st.write(s["evidence_tip"])
            if show_debug:
                st.caption(s["terms_debug"])

    # Missing skills
    jd_skills = extract_skills(jd_raw)
    resume_skills = extract_skills(resume_raw)
    missing = jd_skills - resume_skills
    grouped = categorize_missing(missing)

    st.markdown("### Skill Evidence (where skills appear in your resume)")
    present_skills = sorted(list(resume_skills))
    jd_skill_list = sorted(list(jd_skills))

    tab1, tab2 = st.tabs(["Skills found in Resume", "Skills from JD (evidence in resume)"])

    with tab1:
        st.write(present_skills if present_skills else ["None detected"])

    with tab2:
        if not jd_skill_list:
            st.info("No JD skills detected by the keyword list.")
        else:
            ev = find_skill_evidence(resume_raw, jd_skill_list, max_hits_per_skill=3)
            for sk in jd_skill_list:
                with st.expander(sk):
                    if sk in ev:
                        for ln in ev[sk]:
                            st.write(f"- {ln}")
                    else:
                        st.write("_Not found in resume_ ✅ (add evidence if you have it)")


    st.markdown("### Missing Skills (based on keyword detection)")
    c1, c2, c3 = st.columns(3)
    c1.write("**Core**")
    c1.write(grouped["core"] if grouped["core"] else ["None detected ✅"])
    c2.write("**Tools/Platforms**")
    c2.write(grouped["tools"] if grouped["tools"] else ["None detected ✅"])
    c3.write("**Nice-to-have**")
    c3.write(grouped["nice_to_have"] if grouped["nice_to_have"] else ["None detected ✅"])

    st.markdown("### ATS checks")
    ats = ats_checks(resume_raw)

    if ats["warnings"]:
        st.warning("Potential ATS issues:")
        for w in ats["warnings"]:
            st.write(f"- {w}")
    else:
        st.success("No major ATS issues detected by these simple checks.")

    if ats["tips"]:
        st.info("Suggestions:")
        for tip in ats["tips"]:
            st.write(f"- {tip}")

    st.markdown("### Export report")
    report = build_report(overall_100, section_scores, jd_to_best, grouped)
    report_json = json.dumps(report, indent=2)

    st.download_button(
        label="Download JSON report",
        data=report_json,
        file_name="resume_jd_report.json",
        mime="application/json",
    )

    if show_debug:
        st.code(report_json, language="json")

    if show_debug:
        st.markdown("## Debug")
        st.write("JD chunks:", jd_chunks[:10])
        st.write("Resume chunks:", resume_chunks_for_match[:10])
