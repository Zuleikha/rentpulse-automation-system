"""
CLI entry point: run the job hunt agent.

Usage:
    python run_job_hunt.py

Saves results to:
    data/jobs/jobs.json      — full job list
    data/jobs/jobs.csv       — same data for Excel
    data/jobs/summary.json   — top matches + stats

To record an application:
    from app.agents.job_hunter import mark_applied
    mark_applied("ML Engineer", "Acme Corp", notes="Applied via LinkedIn")
"""
import logging
from dotenv import load_dotenv

load_dotenv()

from app.utils.local_storage import ensure_dirs
ensure_dirs()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s - %(message)s",
)

if __name__ == "__main__":
    from app.agents.job_hunter import run_job_hunt

    summary = run_job_hunt()

    print("\n=== Job Hunt Complete ===")
    print(f"Total jobs found : {summary['total_found']}")
    print(f"Avg fit score    : {summary['avg_fit_score']}/10")
    print(f"Generated at     : {summary['generated_at']}")

    if summary["best_matches"]:
        print("\nTop matches:")
        for job in summary["best_matches"]:
            score = job.get("fit_score", "?")
            title = job.get("title", "")
            company = job.get("company", "")
            print(f"  [{score}/10] {title} — {company}")

    print("\nResults saved to data/jobs/")
