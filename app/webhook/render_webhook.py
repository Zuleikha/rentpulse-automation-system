"""
Production Stripe webhook for Render.

Route: POST /api/stripe/webhook
- Reads raw body for Stripe signature verification
- Verifies using STRIPE_WEBHOOK_SECRET (HMAC-SHA256, no Stripe SDK required)
- Only processes checkout.session.completed
- Delegates to handle_payment_event() — same logic as local webhook

Env vars required:
    STRIPE_WEBHOOK_SECRET   — from Stripe dashboard → Webhooks → signing secret
"""
import hashlib
import hmac
import logging
import os
import time

from flask import Flask, request, jsonify

from app.agents.payment_handler import handle_payment_event

app = Flask(__name__)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


# ── Signature verification ────────────────────────────────────────────────────

def _verify_stripe_signature(raw_body: bytes, sig_header: str, secret: str) -> bool:
    """
    Manually verify Stripe-Signature header using HMAC-SHA256.
    Stripe format: t=timestamp,v1=signature
    Signed payload: f"{timestamp}.{raw_body}"
    Tolerance: 5 minutes.
    """
    try:
        parts = dict(item.split("=", 1) for item in sig_header.split(","))
        timestamp = parts.get("t", "")
        expected_sig = parts.get("v1", "")

        if not timestamp or not expected_sig:
            return False

        # Reject events older than 5 minutes
        if abs(time.time() - int(timestamp)) > 300:
            logging.warning("Stripe webhook timestamp too old — rejecting")
            return False

        signed_payload = f"{timestamp}.".encode() + raw_body
        computed = hmac.new(
            secret.encode("utf-8"),
            signed_payload,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(computed, expected_sig)

    except Exception as e:
        logging.warning(f"Signature verification error: {e}")
        return False


# ── Route ─────────────────────────────────────────────────────────────────────

@app.route("/api/stripe/webhook", methods=["POST"])
def stripe_webhook():
    logging.info("Stripe webhook received")

    secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        logging.error("STRIPE_WEBHOOK_SECRET not set")
        return jsonify({"error": "server misconfiguration"}), 500

    raw_body = request.get_data()
    sig_header = request.headers.get("Stripe-Signature", "")

    if not _verify_stripe_signature(raw_body, sig_header, secret):
        logging.warning("Stripe signature verification failed")
        return jsonify({"error": "invalid signature"}), 400

    logging.info("Stripe signature verified")

    try:
        event = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid JSON"}), 400

    if not isinstance(event, dict):
        return jsonify({"error": "event must be a JSON object"}), 400

    # Only process checkout.session.completed — ignore everything else silently
    if event.get("type") != "checkout.session.completed":
        return jsonify({"skipped": "event type not handled"}), 200

    result = handle_payment_event(event)
    return jsonify(result), 200
