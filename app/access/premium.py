"""
Premium access gate (scaffold).

Reads premium_status from local user storage — no Stripe dependency.
When a real payment succeeds, user_linker.link_payment_to_user() already
sets premium_status=True on the user record, so this gate works automatically
once the Stripe webhook is live.

To grant premium locally for testing, run once:
    python -c "
    from app.agents.user_linker import create_user_if_missing, link_payment_to_user
    create_user_if_missing('you@example.com')
    link_payment_to_user('test_session_01', 'you@example.com')
    print('Done — you@example.com is now premium')
    "

To disable gating entirely (treat all users as premium):
    Set PREMIUM_ENABLED=false in .env
"""
import os


def is_premium_user(email: str) -> bool:
    """
    Return True if the user has premium access.

    Returns True when:
    - PREMIUM_ENABLED env var is set to 'false' (gate disabled globally), or
    - the user record for this email has premium_status=True in local storage.

    Returns False if email is blank or the user record is not found.
    """
    if os.getenv("PREMIUM_ENABLED", "true").lower() != "true":
        return True  # gating disabled — all users treated as premium

    if not email:
        return False

    from app.agents.user_linker import get_user_by_email
    user = get_user_by_email(email)
    return bool(user and user.get("premium_status") is True)


def require_premium(email: str) -> tuple[bool, str]:
    """
    Check premium access for a user email.

    Returns (True, "") if the user has premium access.
    Returns (False, "upgrade_required") if not.

    Usage:
        allowed, reason = require_premium(email)
        if not allowed:
            return {"error": reason}  # or a limited free response
    """
    if is_premium_user(email):
        return True, ""
    return False, "upgrade_required"
