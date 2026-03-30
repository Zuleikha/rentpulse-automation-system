"""
Storage interface for payments and customers.

All callers import from here:
    from app.storage import save_payment, get_payments, save_customer, get_customers

Current backend: JSON files in data/
Future backend:  To swap to Supabase, implement the four functions below in a
                 new module (e.g. app/storage/supabase_backend.py) and replace
                 the two import lines here. Nothing else in the codebase changes.
"""
from app.storage.payments import save_payment, get_payments
from app.storage.customers import save_customer, get_customers

__all__ = ["save_payment", "get_payments", "save_customer", "get_customers"]
