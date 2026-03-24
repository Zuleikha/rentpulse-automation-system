"""
CLI entry point: run the Gmail support triage agent.

Usage:
    python run_support_triage.py

Fetches unseen Gmail messages, classifies them, and saves to:
    data/support/support_tickets.json

Requires in .env:
    GMAIL_ADDRESS       — your Gmail address
    GMAIL_APP_PASSWORD  — Gmail app password (not your account password)
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
    from app.agents.support_triage import run_support_triage

    summary = run_support_triage()

    print("\n=== Support Triage Complete ===")
    print(f"Fetched  : {summary['fetched']}")
    print(f"New      : {summary['new']}")
    print(f"Skipped  : {summary['skipped']} (duplicates)")
    print("\nResults saved to data/support/support_tickets.json")
