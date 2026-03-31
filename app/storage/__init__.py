"""
Storage interface for payments, customers, and users.

All callers import from here:
    from app.storage import save_payment, get_payments, save_customer, get_customers
    from app.storage import save_user, get_users, update_user

Current backend: JSON files in data/
Future backend:  To swap to Supabase, implement the functions below in a
                 new module (e.g. app/storage/supabase_backend.py) and replace
                 the import lines here. Nothing else in the codebase changes.
"""
from app.storage.payments import save_payment, get_payments
from app.storage.customers import save_customer, get_customers
from app.storage.users import save_user, get_users, update_user

__all__ = [
    "save_payment", "get_payments",
    "save_customer", "get_customers",
    "save_user", "get_users", "update_user",
]
