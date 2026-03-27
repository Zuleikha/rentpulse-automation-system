"""
Central agent scheduler.

Schedules all automation agents using the existing `schedule` library.
Each job is wrapped independently — one failure does not stop the others.

Default schedule (all configurable via env vars):
  support_triage      — daily at SUPPORT_TRIAGE_TIME   (default 07:30)
  rentpulse_research  — every N days at RESEARCH_TIME  (default every 2 days at 08:00)
  job_hunter          — Mon + Thu at JOB_HUNT_TIME      (default 08:30)

Run via:
    python run_scheduler.py
"""
import logging
import os
import time

import schedule

logger = logging.getLogger("agent-scheduler")

# ── Schedule config (env-overridable) ─────────────────────────────────────────

SUPPORT_TRIAGE_TIME   = os.getenv("SUPPORT_TRIAGE_TIME",  "07:30")
RESEARCH_TIME         = os.getenv("RESEARCH_TIME",         "08:00")
RESEARCH_INTERVAL_DAYS = int(os.getenv("RESEARCH_INTERVAL_DAYS", "2"))
JOB_HUNT_TIME         = os.getenv("JOB_HUNT_TIME",        "08:30")
JOB_HUNT_DAYS         = os.getenv("JOB_HUNT_DAYS", "monday,thursday").lower().split(",")


# ── Job wrappers ──────────────────────────────────────────────────────────────

def job_support_triage():
    logger.info("[support_triage] Starting scheduled run")
    try:
        from app.agents.support_triage import run_support_triage
        summary = run_support_triage()
        logger.info(
            f"[support_triage] Done — fetched={summary['fetched']} "
            f"new={summary['new']} skipped={summary['skipped']}"
        )
    except Exception as e:
        logger.error(f"[support_triage] Failed: {e}")


def job_rentpulse_research():
    logger.info("[rentpulse_researcher] Starting scheduled run")
    try:
        from app.agents.rentpulse_researcher import run_all_research
        results = run_all_research()
        counts = {task: len(items) for task, items in results.items()}
        logger.info(f"[rentpulse_researcher] Done — {counts}")
    except Exception as e:
        logger.error(f"[rentpulse_researcher] Failed: {e}")


def job_job_hunter():
    logger.info("[job_hunter] Starting scheduled run")
    try:
        from app.agents.job_hunter import run_job_hunt
        summary = run_job_hunt()
        logger.info(
            f"[job_hunter] Done — total={summary['total_found']} "
            f"avg_score={summary['avg_fit_score']}"
        )
    except Exception as e:
        logger.error(f"[job_hunter] Failed: {e}")


# ── Schedule registration ─────────────────────────────────────────────────────

_DAY_MAP = {
    "monday":    schedule.every().monday,
    "tuesday":   schedule.every().tuesday,
    "wednesday": schedule.every().wednesday,
    "thursday":  schedule.every().thursday,
    "friday":    schedule.every().friday,
    "saturday":  schedule.every().saturday,
    "sunday":    schedule.every().sunday,
}


def register_schedules():
    # support_triage — daily
    schedule.every().day.at(SUPPORT_TRIAGE_TIME).do(job_support_triage)
    logger.info(f"Scheduled support_triage: daily at {SUPPORT_TRIAGE_TIME}")

    # rentpulse_researcher — every N days
    schedule.every(RESEARCH_INTERVAL_DAYS).days.at(RESEARCH_TIME).do(job_rentpulse_research)
    logger.info(
        f"Scheduled rentpulse_researcher: every {RESEARCH_INTERVAL_DAYS} day(s) at {RESEARCH_TIME}"
    )

    # job_hunter — specified days of the week
    for day in JOB_HUNT_DAYS:
        day = day.strip()
        if day in _DAY_MAP:
            _DAY_MAP[day].at(JOB_HUNT_TIME).do(job_job_hunter)
            logger.info(f"Scheduled job_hunter: {day} at {JOB_HUNT_TIME}")
        else:
            logger.warning(f"Unknown day in JOB_HUNT_DAYS: '{day}' — skipped")


def run(loop: bool = True):
    """Register all schedules and start the loop."""
    register_schedules()
    logger.info("Agent scheduler running. Press Ctrl+C to stop.")
    if not loop:
        return  # for testing — register only, do not block
    while True:
        schedule.run_pending()
        time.sleep(30)
