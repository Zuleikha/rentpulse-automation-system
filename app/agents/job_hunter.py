"""
Job Hunter agent.

Searches for real, currently active software/AI/ML engineering roles in Ireland
using Claude with live web search. Results saved to data/jobs/.

Profile framing:
- Transitioning into AI/ML from software development
- Strong matches across AI/ML, backend, and data roles
- Not targeting one specific industry — matches on role fit
- Does NOT frame the person as moving into pharmacy or any single sector
"""
import logging
from datetime import datetime

from app.agents.agent_service import run_agent_task, extract_json
from app.utils.local_storage import (
    JOBS_DIR,
    write_json,
    write_csv,
    append_csv_row,
    read_json,
)

# ---- System prompt ----

JOB_HUNT_SYSTEM = """You are a job search agent helping a software developer find
active engineering roles in Ireland.

Candidate profile:
- Background: Software development — Python, backend APIs, data pipelines, REST APIs
- Career direction: Transitioning into AI/ML engineering from software development
- Location: Ireland — Dublin preferred, open to hybrid or remote
- NOT targeting one specific industry — matching purely on role fit and skills
- Strong target roles: ML Engineer, AI Engineer, Backend Engineer (ML/AI components),
  Data Engineer, Data Scientist, MLOps Engineer, Python Developer (AI/data focus),
  Software Engineer at AI companies

Constraints you must follow:
- Do not say the person is moving into pharmacy
- Do not frame the search as targeting one specific industry
- All apply_angle text must describe transitioning from software development into AI/ML
- Prioritise role fit and transferable skills above anything else
- Every job returned must be a REAL, currently listed vacancy you found via search
- Do not invent or hallucinate job listings
"""

# ---- Search prompt ----
# Instructs Claude to actively use web_search and return only real findings.

JOB_SEARCH_PROMPT = """Use web search to find real, currently active job listings
in Ireland for software engineers and AI/ML roles.

Run searches on these sites (use multiple queries):
- linkedin.com/jobs — search "ML engineer Ireland", "AI engineer Dublin",
  "machine learning engineer ireland", "data engineer python ireland",
  "backend engineer AI ireland"
- indeed.ie or indeed.com — search "machine learning engineer ireland",
  "AI developer ireland", "data scientist dublin", "python engineer ireland"
- irishjobs.ie — search "software engineer AI", "machine learning", "data engineer"
- jobs.ie — search "AI engineer", "ML engineer ireland"
- Google — search 'site:linkedin.com/jobs "machine learning" OR "AI engineer" ireland'

For each REAL job listing you find, extract:
- Exact job title as posted
- Company name
- Location (Dublin / Cork / Remote / Hybrid — be specific)
- Employment type (Full-time / Contract / Part-time)
- The job URL
- Where you found it

After collecting real listings, score each one for fit against this profile:
a software developer with Python, backend, and data pipeline experience who is
transitioning into AI/ML. Score 1-10 where 10 = perfect match.

Write a specific apply_angle for each job that explains how to position
the application as a software developer moving into AI/ML — be specific
to that role's requirements, not generic.

Return ONLY a JSON array — no prose before or after, no markdown fences:
[
  {
    "title": "exact job title from the listing",
    "company": "company name",
    "location": "Dublin / Remote / Hybrid / Cork etc",
    "type": "Full-time or Contract or Part-time",
    "fit_score": 8,
    "fit_reason": "specific reason this role fits a Python backend dev moving into AI/ML",
    "apply_angle": "how to frame the application for this specific role — mention the transition from software dev to AI/ML",
    "url": "full URL to the job listing",
    "source": "LinkedIn / Indeed / IrishJobs / Jobs.ie / Company site"
  }
]

Return only jobs you actually found. Do not invent listings.
If you found fewer than 5, return what you found.
Sort by fit_score descending.
"""


def run_job_hunt() -> dict:
    """
    Search for real active jobs in Ireland and save results to data/jobs/.
    Returns the summary dict.
    """
    logging.info("Starting job hunt agent (live web search)...")

    jobs = []
    try:
        response = run_agent_task(
            task=JOB_SEARCH_PROMPT,
            system=JOB_HUNT_SYSTEM,
            model="claude-sonnet-4-6",
            max_tokens=8000,
            use_web_search=True,
        )

        parsed = extract_json(response)

        if isinstance(parsed, list):
            jobs = [j for j in parsed if _is_valid_job(j)]
        elif isinstance(parsed, dict) and "jobs" in parsed:
            jobs = [j for j in parsed["jobs"] if _is_valid_job(j)]

    except Exception as e:
        logging.error(f"Job hunt failed: {e}")
        jobs = []

    now = datetime.now().isoformat()
    best_matches = sorted(jobs, key=lambda j: j.get("fit_score", 0), reverse=True)[:5]
    total = len(jobs)
    avg_score = round(sum(j.get("fit_score", 0) for j in jobs) / max(total, 1), 1)

    summary = {
        "generated_at": now,
        "total_found": total,
        "best_matches": best_matches,
        "avg_fit_score": avg_score,
    }

    write_json(JOBS_DIR / "jobs.json", jobs)
    write_json(JOBS_DIR / "summary.json", summary)

    if jobs:
        _write_jobs_csv(jobs)

    logging.info(f"Job hunt complete: {total} real jobs saved to data/jobs/")
    return summary


def mark_applied(job_title: str, company: str, notes: str = "") -> None:
    """
    Record that you applied to a job.
    Writes to both job_tracker.csv (spreadsheet) and job_tracker.json (dashboard).
    """
    row = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "title": job_title,
        "company": company,
        "status": "applied",
        "notes": notes,
    }

    append_csv_row(
        JOBS_DIR / "job_tracker.csv",
        row,
        fieldnames=["date", "title", "company", "status", "notes"],
    )

    tracker = read_json(JOBS_DIR / "job_tracker.json")
    if not isinstance(tracker, list):
        tracker = []
    row["saved_at"] = datetime.now().isoformat()
    tracker.append(row)
    write_json(JOBS_DIR / "job_tracker.json", tracker)

    logging.info(f"Marked applied: {job_title} at {company}")


# ---- Private helpers ----

def _is_valid_job(j: dict) -> bool:
    """Reject obviously hallucinated or empty entries."""
    return bool(j.get("title") and j.get("company"))


def _write_jobs_csv(jobs: list) -> None:
    fieldnames = [
        "title", "company", "location", "type",
        "fit_score", "fit_reason", "apply_angle", "url", "source",
    ]
    rows = [{k: job.get(k, "") for k in fieldnames} for job in jobs]
    write_csv(JOBS_DIR / "jobs.csv", rows, fieldnames)
