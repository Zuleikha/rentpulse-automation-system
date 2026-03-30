"""
Candidate CV profile used for lightweight job-to-CV matching.
Edit CANDIDATE_PROFILE to reflect your actual skills and background.
"""

CANDIDATE_PROFILE = {
    "skills": [
        "Python", "REST APIs", "backend development", "data pipelines",
        "SQL", "machine learning", "AI", "LLM", "NLP",
        "FastAPI", "Flask", "Docker", "cloud", "AWS", "Azure",
        "MLOps", "pandas", "scikit-learn", "TensorFlow", "PyTorch",
        "data engineering", "CI/CD", "testing", "API integration",
    ],
    "experience_years": 4,
    "location": "Ireland",
    "role_targets": [
        "ML Engineer", "AI Engineer", "Backend Engineer",
        "Data Engineer", "Data Scientist", "MLOps Engineer",
        "Python Developer", "Software Engineer",
    ],
}

# Keywords that are commonly required in AI/ML roles — used to surface gaps.
_TARGET_KEYWORDS = [
    "python", "machine learning", "ml", "ai", "nlp", "llm",
    "data", "backend", "api", "cloud", "mlops", "pytorch",
    "tensorflow", "scikit", "pipeline", "docker", "sql",
]


def cv_match_score(job: dict) -> dict:
    """
    Compute a lightweight CV match for a job dict.
    Returns cv_match_score (1-10), matching_reasons, missing_keywords.
    Does not call any external API — purely local keyword comparison.
    """
    profile_skills = CANDIDATE_PROFILE["skills"]
    job_text = " ".join([
        job.get("title", ""),
        job.get("fit_reason", ""),
        job.get("apply_angle", ""),
        job.get("company", ""),
    ]).lower()

    matched = [s for s in profile_skills if s.lower() in job_text]
    missing = [kw for kw in _TARGET_KEYWORDS if kw not in job_text]

    # Blend the agent's fit_score with keyword overlap for a composite score.
    fit = job.get("fit_score", 5)
    overlap_bonus = min(len(matched), 4)          # up to +4 from keyword hits
    raw = (fit * 0.7) + (overlap_bonus * 0.75)    # weighted blend
    score = max(1, min(10, round(raw)))

    return {
        "cv_match_score":   score,
        "matching_reasons": matched[:6] if matched else ["No direct keyword overlap found"],
        "missing_keywords": missing[:5],
    }
