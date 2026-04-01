"""
User-account linking layer.

Provides reusable, local-only functions to create user records and link
payment sessions to those records.

No automation — call these functions explicitly from payment_actions or
test scripts. No live triggers, no webhooks.

Public interface:
    create_user_if_missing(email: str) -> dict
    link_payment_to_user(session_id: str, email: str) -> bool
    get_user_by_email(email: str) -> dict | None
    get_user_payments(email: str) -> list

User record structure:
    {
        "user_id":                     "usr_<12-char hex>",
        "email":                       "user@example.com",
        "created_at":                  "<ISO-8601 UTC>",
        "premium_status":              false,
        "linked_payment_session_ids":  [],
        "notes":                       ""
    }
"""
import uuid
from datetime import datetime, timezone

from app.storage import save_user, get_users, update_user


def create_user_if_missing(email: str) -> dict:
    """
    Return the existing user record for this email, or create a new one.
    Returns an empty dict if email is blank.
    Never raises.
    """
    if not email:
        return {}

    existing = get_user_by_email(email)
    if existing:
        return existing

    user = {
        "user_id":                    f"usr_{uuid.uuid4().hex[:12]}",
        "email":                      email,
        "created_at":                 datetime.now(timezone.utc).isoformat(),
        "premium_status":             False,
        "linked_payment_session_ids": [],
        "notes":                      "",
    }
    save_user(user)
    return user


def link_payment_to_user(session_id: str, email: str) -> bool:
    """
    Add session_id to the user's linked_payment_session_ids list and set
    premium_status to True.

    - Creates the user record first if it does not exist.
    - Skips silently if session_id is blank, email is blank, or the
      session_id is already linked (idempotent).
    - Returns True if the link was newly added, False otherwise.
    """
    if not session_id or not email:
        return False

    create_user_if_missing(email)

    users = get_users()
    for user in users:
        if user.get("email") == email:
            ids = user.get("linked_payment_session_ids", [])
            if session_id in ids:
                return False
            ids.append(session_id)
            return update_user(email, {
                "linked_payment_session_ids": ids,
                "premium_status": True,
            })

    return False


def get_user_by_email(email: str) -> dict | None:
    """Return the user record for this email, or None if not found."""
    if not email:
        return None
    for user in get_users():
        if user.get("email") == email:
            return user
    return None


def get_user_payments(email: str) -> list:
    """
    Return the list of payment session IDs linked to this user.
    Returns an empty list if the user does not exist.
    """
    user = get_user_by_email(email)
    if not user:
        return []
    return user.get("linked_payment_session_ids", [])
