"""
Local test helper: payment-to-user linking flow.

Run from the project root:
    python -m tests.test_user_linking

This does NOT touch the real data files. It uses a temporary directory so
existing payments/customers/users data is never modified.

What it demonstrates:
  1. A payment record arrives.
  2. create_user_if_missing(email) creates a user if none exists.
  3. link_payment_to_user(session_id, email) links the session and sets premium.
  4. A duplicate call to link_payment_to_user is safely skipped.
  5. get_user_by_email and get_user_payments return correct results.
  6. Missing email is silently skipped — no crash.
"""
import sys
import json
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Redirect storage paths to a temp dir so tests are fully isolated
# ---------------------------------------------------------------------------

_tmp = tempfile.mkdtemp(prefix="rentpulse_test_")
_tmp_path = Path(_tmp)

# Patch path constants BEFORE importing any storage modules
import app.utils.local_storage as _ls
_ls.USERS_DIR = _tmp_path / "users"
_ls.USERS_DIR.mkdir(parents=True, exist_ok=True)

# Now import the modules under test
from app.agents.user_linker import (
    create_user_if_missing,
    link_payment_to_user,
    get_user_by_email,
    get_user_payments,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _section(title: str) -> None:
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print('-' * 60)


def _assert(condition: bool, msg: str) -> None:
    if condition:
        print(f"  PASS  {msg}")
    else:
        print(f"  FAIL  {msg}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

def test_create_user_if_missing() -> None:
    _section("1. create_user_if_missing — new user")

    email = "alice@example.com"
    user = create_user_if_missing(email)

    _assert(user.get("email") == email, "email matches")
    _assert(user.get("user_id", "").startswith("usr_"), "user_id has prefix")
    _assert(user.get("premium_status") is False, "premium_status starts False")
    _assert(user.get("linked_payment_session_ids") == [], "session list starts empty")
    _assert(user.get("created_at") is not None, "created_at is set")

    _section("1b. create_user_if_missing — idempotent (same user returned)")
    user2 = create_user_if_missing(email)
    _assert(user2.get("user_id") == user.get("user_id"), "same user_id returned")


def test_link_payment_to_user() -> None:
    _section("2. link_payment_to_user — first link sets premium")

    email = "alice@example.com"
    session_id = "cs_test_abc123"

    linked = link_payment_to_user(session_id, email)
    _assert(linked is True, "returns True on first link")

    user = get_user_by_email(email)
    _assert(session_id in user.get("linked_payment_session_ids", []), "session_id stored")
    _assert(user.get("premium_status") is True, "premium_status set to True")

    _section("2b. link_payment_to_user — duplicate skipped")
    linked2 = link_payment_to_user(session_id, email)
    _assert(linked2 is False, "returns False on duplicate")

    user2 = get_user_by_email(email)
    _assert(
        user2.get("linked_payment_session_ids").count(session_id) == 1,
        "session_id appears exactly once"
    )


def test_multiple_sessions() -> None:
    _section("3. Multiple payment sessions linked to one user")

    email = "alice@example.com"
    session2 = "cs_test_xyz789"

    link_payment_to_user(session2, email)
    payments = get_user_payments(email)

    _assert("cs_test_abc123" in payments, "first session still present")
    _assert(session2 in payments, "second session added")
    _assert(len(payments) == 2, "exactly two sessions")


def test_missing_email_skipped() -> None:
    _section("4. Blank email — silently skipped, no crash")

    user = create_user_if_missing("")
    _assert(user == {}, "returns empty dict for blank email")

    linked = link_payment_to_user("cs_test_noemail", "")
    _assert(linked is False, "link returns False for blank email")


def test_get_user_not_found() -> None:
    _section("5. get_user_by_email — unknown email returns None")

    user = get_user_by_email("nobody@example.com")
    _assert(user is None, "returns None for unknown email")

    payments = get_user_payments("nobody@example.com")
    _assert(payments == [], "returns empty list for unknown email")


def test_new_user_created_by_link() -> None:
    _section("6. link_payment_to_user creates user if not yet registered")

    email = "bob@example.com"
    session = "cs_test_bob001"

    # Bob has no record yet — link should auto-create
    linked = link_payment_to_user(session, email)
    _assert(linked is True, "link created Bob's record and linked session")

    user = get_user_by_email(email)
    _assert(user is not None, "Bob's record exists")
    _assert(user.get("premium_status") is True, "Bob is premium")
    _assert(session in user.get("linked_payment_session_ids", []), "Bob's session linked")


# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"\nTest temp dir: {_tmp}")

    test_create_user_if_missing()
    test_link_payment_to_user()
    test_multiple_sessions()
    test_missing_email_skipped()
    test_get_user_not_found()
    test_new_user_created_by_link()

    print(f"\n{'=' * 60}")
    print("  All tests passed.")
    print(f"{'=' * 60}\n")
