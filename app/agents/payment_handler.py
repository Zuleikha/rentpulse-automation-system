"""
Payment event handler.

Accepts a Stripe event dict (from the webhook listener), maps it to a
simplified type, extracts structured fields, deduplicates by id, and saves to:
  data/payments/payment_events.json

No Stripe SDK required — works entirely with the raw event dict.
"""
import logging
from datetime import datetime, timezone

from app.storage import save_payment

# ── Stripe event type → simplified type ──────────────────────────────────────

EVENT_TYPE_MAP: dict = {
    "checkout.session.completed":        "payment_success",
    "payment_intent.succeeded":          "payment_success",
    "invoice.paid":                      "payment_success",
    "payment_intent.payment_failed":     "payment_failed",
    "invoice.payment_failed":            "payment_failed",
    "customer.subscription.deleted":     "cancellation",
    "customer.subscription.updated":     "cancellation",  # downgrades treated as cancellation
}


def _map_type(stripe_event_type: str) -> str:
    """Return simplified event type, or 'other' if not recognised."""
    return EVENT_TYPE_MAP.get(stripe_event_type, "other")


# ── Field extraction ──────────────────────────────────────────────────────────

def _extract_fields(event: dict) -> dict | None:
    """
    Pull relevant fields out of a Stripe event dict.
    Returns None if email is missing (invalid record).
    """
    stripe_event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {})

    email = obj.get("customer_details", {}).get("email", "") or ""
    if not email:
        print("Skipped invalid payment (no email)")
        return None

    session_id = obj.get("id", "")
    amount = obj.get("amount_total", 0) or 0

    return {
        "email":             email,
        "amount":            amount,
        "timestamp":         datetime.now(timezone.utc).isoformat(),
        "session_id":        session_id,
        "type":              _map_type(stripe_event_type),
        "stripe_event_type": stripe_event_type,
    }


# ── Public entry point ────────────────────────────────────────────────────────

def handle_payment_event(event: dict) -> dict:
    """
    Process a single Stripe event dict.
    Returns {"processed": 1, "skipped": 0} or {"processed": 0, "skipped": 1}.
    """
    record = _extract_fields(event)
    if not record:
        return {"processed": 0, "skipped": 1}

    saved = save_payment(record)
    if not saved:
        print(f"Duplicate skipped: {record.get('session_id', '')}")
        return {"processed": 0, "skipped": 1}

    print(f"Saved payment: {record['email']} {record['amount']}")

    if (
        record.get("type") == "payment_success"
        and record.get("stripe_event_type") == "checkout.session.completed"
    ):
        from app.agents.payment_actions import run_payment_success
        run_payment_success(record)

    logging.info(f"Saved payment event {record.get('session_id', '')} → storage")
    return {"processed": 1, "skipped": 0}


# ── Test ──────────────────────────────────────────────────────────────────────

def simulate_checkout_event() -> None:
    """Run a mock checkout.session.completed event through the full flow."""
    mock_event = {
        "id": "evt_test_001",
        "type": "checkout.session.completed",
        "data": {
            "object": {
                "id": "cs_test_session_001",
                "amount_total": 999,
                "customer_details": {
                    "email": "test@example.com"
                }
            }
        }
    }

    print("--- simulate_checkout_event: run 1 (expect save) ---")
    result1 = handle_payment_event(mock_event)
    print(result1)

    print("--- simulate_checkout_event: run 2 (expect duplicate skip) ---")
    result2 = handle_payment_event(mock_event)
    print(result2)
