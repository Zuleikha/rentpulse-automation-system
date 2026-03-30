"""
CLI helper for the job application tracker.

Commands:
    python run_job_tracker.py list
        Show all tracked jobs with status, fit score, and CV match score.

    python run_job_tracker.py import-jobs
        Import all jobs from data/jobs/jobs.json into the tracker.
        Safe to re-run — deduplicates by job_url automatically.

    python run_job_tracker.py shortlist <job_url>
        Mark a tracked job as shortlisted.

    python run_job_tracker.py apply <job_url> [notes]
        Mark a job as applied and record today's date.

    python run_job_tracker.py status <job_url> <status> [notes]
        Update the status of a tracked job.
        Valid statuses: saved | applied | interview | rejected | offer | closed

Examples:
    python run_job_tracker.py import-jobs
    python run_job_tracker.py list
    python run_job_tracker.py shortlist https://ie.indeed.com/...
    python run_job_tracker.py apply https://ie.indeed.com/... "Applied via LinkedIn"
    python run_job_tracker.py status https://ie.indeed.com/... interview "Got a call"
"""
import sys
import logging
from dotenv import load_dotenv

load_dotenv()

from app.utils.local_storage import ensure_dirs, JOBS_DIR, read_json
ensure_dirs()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s - %(message)s")

from app.agents.job_tracker import (
    get_all, get_shortlisted, get_applied,
    shortlist_job, update_status, add_to_tracker,
)


def cmd_list():
    entries = get_all()
    if not entries:
        print("No tracked jobs. Run: python run_job_tracker.py import-jobs")
        return
    print(f"\n{'Status':<12} {'Fit':>4} {'CV':>4} {'SL':<3} Title / Company")
    print("─" * 75)
    for e in entries:
        sl = "★" if e.get("shortlisted") else " "
        title = str(e.get("title", ""))[:32]
        company = str(e.get("company", ""))[:20]
        print(
            f"{e.get('status', ''):<12} "
            f"{e.get('fit_score', '?'):>4} "
            f"{e.get('cv_match_score', '?'):>4} "
            f"{sl:<3} "
            f"{title:<33} {company}"
        )
    print(
        f"\nTotal: {len(entries)}  "
        f"Shortlisted: {len(get_shortlisted())}  "
        f"Applied/Active: {len(get_applied())}"
    )


def cmd_import():
    jobs = read_json(JOBS_DIR / "jobs.json")
    if not isinstance(jobs, list) or not jobs:
        print("No jobs found in data/jobs/jobs.json. Run python run_job_hunt.py first.")
        return
    added = skipped = 0
    for job in jobs:
        entry = add_to_tracker(job)
        # add_to_tracker returns existing entry without 'added_at' mutation if already tracked
        if entry.get("job_url") and entry.get("added_at"):
            added += 1
        else:
            skipped += 1
    print(f"Done. Added: {added}  Already tracked (skipped): {skipped}  Total: {len(get_all())}")


def cmd_shortlist(url):
    ok = shortlist_job(url)
    print("Shortlisted." if ok else f"Not found: {url}")


def cmd_apply(url, notes=""):
    ok = update_status(url, "applied", notes)
    print("Marked as applied." if ok else f"Not found: {url}")


def cmd_status(url, status, notes=""):
    ok = update_status(url, status, notes)
    print(f"Status → {status}." if ok else f"Not found or invalid status: {url}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        cmd_list()
    elif args[0] == "import-jobs":
        cmd_import()
    elif args[0] == "shortlist" and len(args) >= 2:
        cmd_shortlist(args[1])
    elif args[0] == "apply" and len(args) >= 2:
        cmd_apply(args[1], " ".join(args[2:]))
    elif args[0] == "status" and len(args) >= 3:
        cmd_status(args[1], args[2], " ".join(args[3:]))
    else:
        print(__doc__)
