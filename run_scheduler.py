"""
CLI entry point: run the central agent scheduler.

Schedules and runs all automation agents on a recurring basis:
  - support_triage      daily
  - rentpulse_research  every 2 days
  - job_hunter          Monday + Thursday

Manual runners are unaffected:
  python run_job_hunt.py
  python run_rentpulse_research.py
  python run_support_triage.py

Schedule times can be overridden via env vars (see app/scheduler/agent_scheduler.py).

Usage:
    python run_scheduler.py
"""
import logging
from dotenv import load_dotenv

load_dotenv()

from app.utils.local_storage import ensure_dirs
ensure_dirs()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)

if __name__ == "__main__":
    from app.scheduler.agent_scheduler import run
    run()
