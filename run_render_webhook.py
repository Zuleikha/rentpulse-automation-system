"""
CLI entry point: run the production Stripe webhook server for Render.

Render sets the PORT env var automatically.
Binds to 0.0.0.0 so Render can route traffic to it.

Usage (local):
    python run_render_webhook.py

Usage (Render start command):
    python run_render_webhook.py

Requires in environment:
    STRIPE_WEBHOOK_SECRET   — Stripe webhook signing secret
    STRIPE_SECRET_KEY       — Stripe secret key (available for future use)
"""
import os

from dotenv import load_dotenv
load_dotenv()

from app.utils.local_storage import ensure_dirs
ensure_dirs()

if __name__ == "__main__":
    from app.webhook.render_webhook import app

    port = int(os.getenv("PORT", 8766))
    print(f"RentPulse Stripe webhook (Render) listening on port {port}")
    app.run(host="0.0.0.0", port=port)
