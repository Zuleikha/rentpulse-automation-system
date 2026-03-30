"""
Job application tracker.

Stores tracked/shortlisted/applied jobs in data/jobs/job_applications.json.
Deduplicates by job_url. Provides helpers for shortlisting and status updates.
CV match score is computed locally (no API call) via cv_profile.cv_match_score.

Status values: saved | applied | interview | rejected | offer | closed
"""
import logging
from datetime import datetime

from app.utils.local_storage import JOBS_DIR, read_json, write_json
from app.agents.cv_profile import cv_match_score

APPLICATIONS_FILE = JOBS_DIR / "job_applications.json"

VALID_STATUSES = {"saved", "applied", "interview", "rejected", "offer", "closed"}


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load() -> list:
    data = read_json(APPLICATIONS_FILE)
    return data if isinstance(data, list) else []


def _save(data: list) -> None:
    write_json(APPLICATIONS_FILE, data)


def _find_by_url(data: list, url: str) -> int:
    """Return index of existing entry with this url, or -1."""
    for i, entry in enumerate(data):
        if entry.get("job_url") == url:
            return i
    return -1


# ── Public API ────────────────────────────────────────────────────────────────

def add_to_tracker(job: dict, status: str = "saved") -> dict:
    """
    Add a job to the tracker. Deduplicates by job_url — if already present
    returns the existing entry unchanged. Computes cv_match_score locally.
    """
    url = job.get("url") or job.get("job_url") or ""
    data = _load()

    if url:
        idx = _find_by_url(data, url)
        if idx >= 0:
            return data[idx]

    match = cv_match_score(job)

    entry = {
        "job_url":          url,
        "title":            job.get("title", ""),
        "company":          job.get("company", ""),
        "source":           job.get("source", ""),
        "location":         job.get("location", ""),
        "date_found":       job.get("date_found", datetime.now().strftime("%Y-%m-%d")),
        "date_applied":     "",
        "status":           status if status in VALID_STATUSES else "saved",
        "shortlisted":      False,
        "notes":            "",
        "fit_score":        job.get("fit_score", 0),
        "cv_match_score":   match["cv_match_score"],
        "matching_reasons": match["matching_reasons"],
        "missing_keywords": match["missing_keywords"],
        "added_at":         datetime.now().isoformat(),
    }

    data.append(entry)
    _save(data)
    logging.info(f"Tracker: added '{entry['title']}' at {entry['company']}")
    return entry


def shortlist_job(job_url: str) -> bool:
    """Mark a job as shortlisted. Returns True if the entry was found."""
    data = _load()
    idx = _find_by_url(data, job_url)
    if idx < 0:
        logging.warning(f"shortlist_job: no entry found for {job_url}")
        return False
    data[idx]["shortlisted"] = True
    _save(data)
    logging.info(f"Shortlisted: {data[idx].get('title')}")
    return True


def update_status(job_url: str, status: str, notes: str = "") -> bool:
    """
    Update application status for a tracked job. Returns True if found.
    Automatically records date_applied when status is set to 'applied'.
    """
    if status not in VALID_STATUSES:
        logging.warning(f"update_status: invalid status '{status}' — use one of {VALID_STATUSES}")
        return False
    data = _load()
    idx = _find_by_url(data, job_url)
    if idx < 0:
        logging.warning(f"update_status: no entry found for {job_url}")
        return False
    data[idx]["status"] = status
    if status == "applied" and not data[idx].get("date_applied"):
        data[idx]["date_applied"] = datetime.now().strftime("%Y-%m-%d")
    if notes:
        data[idx]["notes"] = notes
    _save(data)
    logging.info(f"Status updated → {status}: {data[idx].get('title')}")
    return True


def get_all() -> list:
    """Return all tracked jobs."""
    return _load()


def get_shortlisted() -> list:
    """Return only shortlisted jobs."""
    return [e for e in _load() if e.get("shortlisted")]


def get_applied() -> list:
    """Return jobs with status applied, interview, or offer."""
    return [e for e in _load() if e.get("status") in {"applied", "interview", "offer"}]


def notify_new_jobs(jobs: list, min_score: int = 8) -> None:
    """
    Send a Telegram notification summarising high-fit jobs found.
    Only fires if TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are configured.
    Safe to call unconditionally — notifier checks for missing config internally.
    """
    try:
        from app.scheduler.notifier import send_telegram
        high = [j for j in jobs if j.get("fit_score", 0) >= min_score]
        if not high:
            return
        lines = [f"<b>Job Hunt: {len(high)} high-fit job(s) found</b>"]
        for j in high[:5]:
            lines.append(f"  [{j.get('fit_score')}/10] {j.get('title')} — {j.get('company')}")
        send_telegram("\n".join(lines))
    except Exception as e:
        logging.warning(f"notify_new_jobs: {e}")
