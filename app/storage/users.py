"""
JSON-backed user account storage.

Public interface:
    save_user(user: dict) -> bool
    get_users() -> list
    update_user(email: str, updates: dict) -> bool

user dict must contain 'email'. All other fields are optional.

To swap to Supabase later: implement these three functions in a new module
(e.g. app/storage/supabase_backend.py) and update the imports in __init__.py.
No other files need to change.
"""
from app.utils.local_storage import USERS_DIR, read_json, write_json

_FILE = USERS_DIR / "users.json"


def save_user(user: dict) -> bool:
    """
    Append a new user record to the store.
    Skips if email is empty.
    Deduplicates by email — returns False if already present.
    Returns True if the record was saved.
    """
    email = user.get("email", "")
    if not email:
        return False

    existing = read_json(_FILE)
    if not isinstance(existing, list):
        existing = []

    if any(u.get("email") == email for u in existing):
        return False

    existing.append(user)
    write_json(_FILE, existing)
    return True


def get_users() -> list:
    """Return all stored user records."""
    data = read_json(_FILE)
    return data if isinstance(data, list) else []


def update_user(email: str, updates: dict) -> bool:
    """
    Merge updates into an existing user record by email.
    Returns True if found and updated, False if not found.
    """
    if not email:
        return False

    existing = read_json(_FILE)
    if not isinstance(existing, list):
        return False

    for user in existing:
        if user.get("email") == email:
            user.update(updates)
            write_json(_FILE, existing)
            return True

    return False
