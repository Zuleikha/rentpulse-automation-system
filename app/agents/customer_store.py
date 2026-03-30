"""
Customer store — thin adapter layer.

Callers (e.g. payment_actions.py) pass a record with 'customer_email'.
This module maps that to the storage interface which uses 'email'.

Storage logic (deduplication, JSON read/write) lives in app.storage.
"""
from app.storage import save_customer as _storage_save_customer


def save_customer(record: dict) -> None:
    """
    Accept a payment record and persist the customer.
    Maps 'customer_email' to 'email' before calling storage.
    Silently skips on empty email or duplicate (matches original behaviour).
    """
    try:
        email = record.get("customer_email", "") or record.get("email", "")
        if not email:
            return
        _storage_save_customer({
            "email":  email,
            "amount": record.get("amount", 0),
        })
    except Exception:
        pass
