"""
JSON-backed payment storage.

Public interface:
    save_payment(payment: dict) -> bool
    get_payments() -> list

To swap to Supabase later: implement these two functions in a new module
(e.g. app/storage/supabase_backend.py) and update the imports in __init__.py.
No other files need to change.
"""
from app.utils.local_storage import PAYMENTS_DIR, read_json, write_json

_FILE = PAYMENTS_DIR / "payment_events.json"


def save_payment(payment: dict) -> bool:
    """
    Append a payment record to the store.
    Deduplicates by session_id — returns False if already present.
    Returns True if the record was saved.
    """
    existing = read_json(_FILE)
    if not isinstance(existing, list):
        existing = []

    session_id = payment.get("session_id", "")
    if session_id:
        seen = {e.get("session_id") for e in existing if e.get("session_id")}
        if session_id in seen:
            return False

    existing.append(payment)
    write_json(_FILE, existing)
    return True


def get_payments() -> list:
    """Return all stored payment records."""
    data = read_json(_FILE)
    return data if isinstance(data, list) else []
