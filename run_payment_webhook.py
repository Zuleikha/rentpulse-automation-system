"""
CLI entry point: run the Stripe payment webhook server.

Usage:
    python run_payment_webhook.py

Listens for Stripe webhook events on port 8765 and saves to:
    data/payments/

Requires in .env:
    STRIPE_WEBHOOK_SECRET  — Stripe webhook signing secret
"""
from dotenv import load_dotenv

load_dotenv()

from app.utils.local_storage import ensure_dirs
ensure_dirs()

if __name__ == "__main__":
    from app.webhook.stripe_webhook import start_server

    print("Stripe webhook listening on port 8765")
    start_server(port=8765)
