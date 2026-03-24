"""
Payment event handler.

Accepts a Stripe event dict (from the webhook listener), maps it to a
simplified type, extracts structured fields, deduplicates by id, and saves to:
  data/payments/payment_events.json

No Stripe SDK required — works entirely with the raw event dict.
"""
import logging
from datetime import datetime, timezone

from app.utils.local_storage import PAYMENTS_DIR, read_json, write_json

EVENTS_FILE = PAYMENTS_DIR / "payment_events.json"

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

def _extract_fields(event: dict) -> dict:
    """
    Pull relevant fields out of a Stripe event dict.
    Handles checkout sessions, payment intents, invoices, and subscriptions.
    Falls back to empty strings / 0 if a field is absent.
    """
    stripe_event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {})

    # Amount — Stripe stores cents; keep as-is (dashboard can format)
    amount = (
        obj.get("amount_total")       # checkout.session
        or obj.get("amount")          # payment_intent
        or obj.get("amount_due")      # invoice
        or obj.get("plan", {}).get("amount", 0)   # subscription
        or 0
    )

    currency = obj.get("currency", "")

    # Customer email — present on checkout sessions and invoices directly
    customer_email = (
        obj.get("customer_email")
        or obj.get("customer_details", {}).get("email", "")
        or ""
    )

    customer_id = obj.get("customer", "")

    return {
        "id":                event.get("id", ""),
        "type":              _map_type(stripe_event_type),
        "amount":            amount,
        "currency":          currency,
        "customer_email":    customer_email,
        "customer_id":       customer_id,
        "status":            "processed",
        "stripe_event_type": stripe_event_type,
        "received_at":       datetime.now(timezone.utc).isoformat(),
    }


# ── Deduplicate & save ────────────────────────────────────────────────────────

def _load_seen_ids() -> set:
    """Return set of all event ids already saved."""
    existing = read_json(EVENTS_FILE)
    if not isinstance(existing, list):
        return set()
    return {e["id"] for e in existing if e.get("id")}


def _save_event(record: dict) -> None:
    """Append one event record to the JSON array on disk."""
    existing = read_json(EVENTS_FILE)
    if not isinstance(existing, list):
        existing = []
    existing.append(record)
    write_json(EVENTS_FILE, existing)


# ── Public entry point ────────────────────────────────────────────────────────

def handle_payment_event(event: dict) -> dict:
    """
    Process a single Stripe event dict.
    Returns {"processed": 1, "skipped": 0} or {"processed": 0, "skipped": 1}.
    """
    event_id = event.get("id", "")
    event_type = event.get("type", "unknown")

    if not event_id:
        logging.warning("Received payment event with no id — skipping")
        return {"processed": 0, "skipped": 1}

    seen = _load_seen_ids()
    if event_id in seen:
        logging.info(f"Duplicate event {event_id} — skipped")
        return {"processed": 0, "skipped": 1}

    record = _extract_fields(event)
    _save_event(record)
    logging.info(f"Saved payment event {event_id} ({event_type}) → {EVENTS_FILE}")
    return {"processed": 1, "skipped": 0}
