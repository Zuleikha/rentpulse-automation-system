"""
End-to-end validation: premium gating (Stage 8).

Run from the project root:
    python -m tests.test_premium_gating

Covers:
  1. is_premium_user / require_premium with free user
  2. is_premium_user / require_premium with premium user
  3. PREMIUM_ENABLED=false bypasses all gating
  4. Blank email always denied
  5. scam_detector gating (free blocked, premium allowed)
  6. rentpulse_researcher gating (leads/competitors blocked for free user)
  7. rentpulse_researcher allows free tasks (content_ideas, complaints)
  8. Scheduler context (no email) bypasses researcher gate
  9. Full payment -> user -> premium flow end-to-end
 10. Webhook: render_webhook Flask app responds correctly

Uses an isolated temp directory — no real data files are touched.
"""
import os
import sys
import json
import tempfile
import importlib
from pathlib import Path
from unittest.mock import patch, MagicMock

# ---------------------------------------------------------------------------
# Redirect ALL storage to a temp dir before importing anything
# ---------------------------------------------------------------------------

_tmp = Path(tempfile.mkdtemp(prefix="rp_test_gating_"))

import app.utils.local_storage as _ls
_ls.USERS_DIR     = _tmp / "users"
_ls.PAYMENTS_DIR  = _tmp / "payments"
_ls.CUSTOMERS_DIR = _tmp / "customers"
_ls.RENTPULSE_DIR = _tmp / "rentpulse"
for d in [_ls.USERS_DIR, _ls.PAYMENTS_DIR, _ls.CUSTOMERS_DIR, _ls.RENTPULSE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Now import modules under test
from app.access.premium import is_premium_user, require_premium
from app.agents.user_linker import (
    create_user_if_missing,
    link_payment_to_user,
    get_user_by_email,
)
from app.agents.scam_detector import detect_scam
from app.agents.rentpulse_researcher import (
    run_research_task,
    PREMIUM_RESEARCH_TASKS,
)

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

_results: list[dict] = []

def _check(name: str, condition: bool, detail: str = "") -> None:
    status = "PASS" if condition else "FAIL"
    msg = f"  [{status}] {name}"
    if detail:
        msg += f" — {detail}"
    print(msg)
    _results.append({"name": name, "passed": condition, "detail": detail})
    if not condition:
        # Don't exit immediately; collect all failures first
        pass

def _section(title: str) -> None:
    print(f"\n{'-' * 64}")
    print(f"  {title}")
    print(f"{'-' * 64}")

# Test emails
FREE_EMAIL    = "free@example.com"
PREMIUM_EMAIL = "premium@example.com"
BLANK_EMAIL   = ""

# ---------------------------------------------------------------------------
# Test 1: Free user — is_premium_user / require_premium
# ---------------------------------------------------------------------------

def test_free_user_gate():
    _section("1. Free user — is_premium_user / require_premium")

    # User does not exist at all
    result = is_premium_user(FREE_EMAIL)
    _check("is_premium_user (unknown user)", result is False)

    allowed, reason = require_premium(FREE_EMAIL)
    _check("require_premium returns False", allowed is False)
    _check("require_premium reason is 'upgrade_required'", reason == "upgrade_required")

    # Create user explicitly (premium_status starts False)
    create_user_if_missing(FREE_EMAIL)
    result2 = is_premium_user(FREE_EMAIL)
    _check("is_premium_user (created, not linked)", result2 is False)

# ---------------------------------------------------------------------------
# Test 2: Premium user — after linking a payment
# ---------------------------------------------------------------------------

def test_premium_user_gate():
    _section("2. Premium user — after link_payment_to_user")

    create_user_if_missing(PREMIUM_EMAIL)
    link_payment_to_user("cs_test_premium_001", PREMIUM_EMAIL)

    result = is_premium_user(PREMIUM_EMAIL)
    _check("is_premium_user (linked user)", result is True)

    allowed, reason = require_premium(PREMIUM_EMAIL)
    _check("require_premium returns True", allowed is True)
    _check("require_premium reason is empty string", reason == "")

# ---------------------------------------------------------------------------
# Test 3: PREMIUM_ENABLED=false — gate bypassed for everyone
# ---------------------------------------------------------------------------

def test_premium_enabled_false():
    _section("3. PREMIUM_ENABLED=false — gate disabled globally")

    with patch.dict(os.environ, {"PREMIUM_ENABLED": "false"}):
        # Re-import to pick up patched env (function reads os.getenv at call time)
        result_free = is_premium_user(FREE_EMAIL)
        result_unknown = is_premium_user("nobody@example.com")
        result_blank = is_premium_user(BLANK_EMAIL)

    _check("free user treated as premium when gate off", result_free is True)
    _check("unknown user treated as premium when gate off", result_unknown is True)
    _check("blank email treated as premium when gate off", result_blank is True)

# ---------------------------------------------------------------------------
# Test 4: Blank email always denied (when gate is on)
# ---------------------------------------------------------------------------

def test_blank_email():
    _section("4. Blank email — always denied when gate is active")

    with patch.dict(os.environ, {"PREMIUM_ENABLED": "true"}):
        result = is_premium_user(BLANK_EMAIL)
        allowed, reason = require_premium(BLANK_EMAIL)

    _check("is_premium_user('') returns False", result is False)
    _check("require_premium('') returns False", allowed is False)
    _check("require_premium('') reason is 'upgrade_required'", reason == "upgrade_required")

# ---------------------------------------------------------------------------
# Test 5: scam_detector gating
# ---------------------------------------------------------------------------

def test_scam_detector_gating():
    _section("5. scam_detector — premium gate")

    listing = {"url": "https://example.com/listing/1", "price": 800, "description": "Nice flat"}

    # Free user
    result_free = detect_scam(listing, FREE_EMAIL)
    _check("detect_scam free user: allowed=False", result_free["allowed"] is False)
    _check("detect_scam free user: reason='upgrade_required'", result_free["reason"] == "upgrade_required")
    _check("detect_scam free user: is_scam=None", result_free["is_scam"] is None)

    # Premium user
    result_premium = detect_scam(listing, PREMIUM_EMAIL)
    _check("detect_scam premium user: allowed=True", result_premium["allowed"] is True)
    _check("detect_scam premium user: reason='not_implemented'", result_premium["reason"] == "not_implemented")
    _check("detect_scam premium user: is_scam=None (stub)", result_premium["is_scam"] is None)

    # Blank email treated as free
    result_blank = detect_scam(listing, BLANK_EMAIL)
    _check("detect_scam blank email: allowed=False", result_blank["allowed"] is False)

# ---------------------------------------------------------------------------
# Test 6: researcher gating — premium tasks blocked for free user
# ---------------------------------------------------------------------------

def test_researcher_premium_tasks_blocked():
    _section("6. Researcher — premium tasks blocked for free user")

    for task in PREMIUM_RESEARCH_TASKS:
        result = run_research_task(task, email=FREE_EMAIL)
        _check(
            f"run_research_task('{task}', free user) returns []",
            result == [],
            f"got {result!r}"
        )

# ---------------------------------------------------------------------------
# Test 7: researcher gating — free tasks not blocked for free user
# ---------------------------------------------------------------------------

def test_researcher_free_tasks_not_blocked():
    _section("7. Researcher — free tasks NOT gated (gate skipped, Claude call mocked)")

    free_tasks = [t for t in ["content_ideas", "complaints"] if t not in PREMIUM_RESEARCH_TASKS]
    _check("content_ideas and complaints are not in PREMIUM_RESEARCH_TASKS",
           len(free_tasks) == 2,
           f"free_tasks={free_tasks}")

    # Mock the Claude call so we don't need a real API key
    mock_response = '[{"idea": "test", "platform": "Twitter/X", "angle": "speed_of_listings", "hook": "test hook", "why_now": "test", "estimated_engagement": "medium"}]'
    with patch("app.agents.rentpulse_researcher.run_agent_task", return_value=mock_response):
        for task in free_tasks:
            result = run_research_task(task, email=FREE_EMAIL)
            _check(
                f"run_research_task('{task}', free user) not blocked (returns data)",
                isinstance(result, list),
                f"type={type(result).__name__}, len={len(result)}"
            )

# ---------------------------------------------------------------------------
# Test 8: researcher scheduler context — no email bypasses gate
# ---------------------------------------------------------------------------

def test_researcher_scheduler_context():
    _section("8. Researcher — scheduler context (no email) bypasses premium gate")

    mock_response = '[{"source": "reddit", "signal": "test", "location": "Dublin", "urgency": "high", "angle": "test"}]'
    with patch("app.agents.rentpulse_researcher.run_agent_task", return_value=mock_response):
        for task in PREMIUM_RESEARCH_TASKS:
            result = run_research_task(task)  # no email
            _check(
                f"run_research_task('{task}', no email) runs without gate",
                isinstance(result, list),
                f"type={type(result).__name__}"
            )

# ---------------------------------------------------------------------------
# Test 9: Full end-to-end payment → user → premium flow
# ---------------------------------------------------------------------------

def test_full_payment_flow():
    _section("9. End-to-end: payment -> user created -> premium set")

    email = "newpayer@example.com"
    session = "cs_e2e_test_001"

    # Before payment — user doesn't exist, not premium
    _check("Before payment: not premium", is_premium_user(email) is False)
    _check("Before payment: user is None", get_user_by_email(email) is None)

    # Simulate payment success
    create_user_if_missing(email)
    linked = link_payment_to_user(session, email)
    _check("link_payment_to_user returns True on first link", linked is True)

    # After payment — user exists and is premium
    user = get_user_by_email(email)
    _check("After payment: user record exists", user is not None)
    _check("After payment: premium_status=True", user.get("premium_status") is True)
    _check("After payment: session linked", session in user.get("linked_payment_session_ids", []))
    _check("After payment: is_premium_user=True", is_premium_user(email) is True)

    # Scam detector now allowed
    result = detect_scam({}, email)
    _check("After payment: scam_detector allowed", result["allowed"] is True)

    # Researcher premium tasks now allowed (mock Claude)
    mock_response = '[{"source": "reddit", "signal": "test", "location": "Dublin", "urgency": "high", "angle": "test"}]'
    with patch("app.agents.rentpulse_researcher.run_agent_task", return_value=mock_response):
        for task in PREMIUM_RESEARCH_TASKS:
            result = run_research_task(task, email=email)
            _check(f"After payment: researcher '{task}' allowed", isinstance(result, list) and len(result) > 0)

    # Idempotency — duplicate link is skipped
    linked2 = link_payment_to_user(session, email)
    _check("Duplicate link_payment_to_user returns False", linked2 is False)
    user2 = get_user_by_email(email)
    count = user2.get("linked_payment_session_ids", []).count(session)
    _check("Session appears exactly once after duplicate attempt", count == 1)

# ---------------------------------------------------------------------------
# Test 10: render_webhook Flask app responds correctly
# ---------------------------------------------------------------------------

def test_render_webhook():
    _section("10. render_webhook Flask app — health and signature checks")

    try:
        from app.webhook.render_webhook import app as flask_app
        client = flask_app.test_client()

        # POST with no signature and no secret set — should 500 (secret not configured)
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": ""}):
            resp = client.post(
                "/api/stripe/webhook",
                data=b'{"type":"checkout.session.completed"}',
                content_type="application/json",
            )
            _check(
                "Webhook with no secret returns 500",
                resp.status_code == 500,
                f"status={resp.status_code}"
            )

        # POST with wrong signature — should 400
        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": "whsec_test"}):
            resp = client.post(
                "/api/stripe/webhook",
                data=b'{"type":"checkout.session.completed"}',
                content_type="application/json",
                headers={"Stripe-Signature": "t=1234567890,v1=badhash"},
            )
            _check(
                "Webhook with wrong signature returns 400",
                resp.status_code == 400,
                f"status={resp.status_code}"
            )

        # Non-handled event type — should 200 skipped
        import time, hmac, hashlib
        secret = "whsec_test"
        payload = b'{"type":"payment_intent.created"}'
        ts = str(int(time.time()))
        signed = f"{ts}.".encode() + payload
        sig = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
        sig_header = f"t={ts},v1={sig}"

        with patch.dict(os.environ, {"STRIPE_WEBHOOK_SECRET": secret}):
            resp = client.post(
                "/api/stripe/webhook",
                data=payload,
                content_type="application/json",
                headers={"Stripe-Signature": sig_header},
            )
            body = json.loads(resp.data)
            _check(
                "Unhandled event type returns 200 skipped",
                resp.status_code == 200 and "skipped" in body,
                f"status={resp.status_code} body={body}"
            )

    except Exception as exc:
        _check("render_webhook test setup", False, str(exc))

# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------

def main():
    print(f"\nTest temp dir: {_tmp}")
    print("Running premium gating validation...\n")

    test_free_user_gate()
    test_premium_user_gate()
    test_premium_enabled_false()
    test_blank_email()
    test_scam_detector_gating()
    test_researcher_premium_tasks_blocked()
    test_researcher_free_tasks_not_blocked()
    test_researcher_scheduler_context()
    test_full_payment_flow()
    test_render_webhook()

    # Summary
    total  = len(_results)
    passed = sum(1 for r in _results if r["passed"])
    failed = [r for r in _results if not r["passed"]]

    print(f"\n{'=' * 64}")
    print(f"  Results: {passed}/{total} passed")
    if failed:
        print(f"\n  FAILED ({len(failed)}):")
        for f in failed:
            print(f"    - {f['name']}")
            if f["detail"]:
                print(f"      {f['detail']}")
    else:
        print("  All checks passed.")
    print(f"{'=' * 64}\n")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
