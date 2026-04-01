"""
Scam listing detector — premium only (scaffold).

Gated behind premium access. Detection logic is not yet implemented.
Wire real checks in under the TODO comment below once the feature is ready.

Usage:
    from app.agents.scam_detector import detect_scam

    result = detect_scam(listing, user_email)

    if not result["allowed"]:
        # free user — return upgrade prompt
        return {"error": result["reason"]}

    if result["is_scam"] is None:
        # premium user but detection not yet implemented
        pass
"""
from app.access.premium import is_premium_user


def detect_scam(listing: dict, email: str) -> dict:
    """
    Run scam detection on a listing dict for the given user email.

    Args:
        listing: dict containing listing fields (url, price, description, etc.)
        email:   the requesting user's email — checked against premium_status

    Returns:
        {
            "allowed":  bool,        # False = not premium, block the call
            "is_scam":  bool | None, # None until detection logic is implemented
            "reason":   str,         # "upgrade_required" | "not_implemented" | ""
        }
    """
    if not is_premium_user(email):
        return {"allowed": False, "is_scam": None, "reason": "upgrade_required"}

    # TODO: implement scam detection logic
    # Signals to check:
    # - price significantly below local area average
    # - missing or stock photos
    # - vague or inconsistent location details
    # - unusual contact method (WhatsApp only, no phone)
    # - copy-pasted or templated description text
    # - landlord email domain mismatch
    return {"allowed": True, "is_scam": None, "reason": "not_implemented"}
