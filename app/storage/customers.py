"""
JSON-backed customer storage.

Public interface:
    save_customer(customer: dict) -> bool
    get_customers() -> list

customer dict must contain 'email' and 'amount'. 'timestamp' is optional
and will be set automatically if omitted.

To swap to Supabase later: implement these two functions in a new module
(e.g. app/storage/supabase_backend.py) and update the imports in __init__.py.
No other files need to change.
"""
from datetime import datetime

from app.utils.local_storage import CUSTOMERS_DIR, read_json, write_json

_FILE = CUSTOMERS_DIR / "customers.json"


def save_customer(customer: dict) -> bool:
    """
    Append a customer record to the store.
    Skips if email is empty.
    Deduplicates by email — returns False if already present.
    Returns True if the record was saved.
    """
    email = customer.get("email", "")
    if not email:
        return False

    existing = read_json(_FILE)
    if not isinstance(existing, list):
        existing = []

    if any(c.get("email") == email for c in existing):
        return False

    entry = {
        "email":     email,
        "amount":    customer.get("amount", 0),
        "timestamp": customer.get("timestamp", datetime.utcnow().isoformat()),
    }
    existing.append(entry)
    write_json(_FILE, existing)
    return True


def get_customers() -> list:
    """Return all stored customer records."""
    data = read_json(_FILE)
    return data if isinstance(data, list) else []
