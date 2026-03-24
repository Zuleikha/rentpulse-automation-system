"""
Gmail support triage agent.

Fetches emails via IMAP, classifies them rule-based first (Claude fallback
only if unclear), extracts structured fields, deduplicates, and saves to:
  data/support/support_tickets.json

No extra dependencies — uses stdlib imaplib + email only for Gmail access.
"""
import imaplib
import email
import logging
import os
from datetime import datetime
from email.header import decode_header
from typing import Optional

from app.agents.agent_service import run_agent_task
from app.utils.local_storage import SUPPORT_DIR, read_json, write_json

TICKETS_FILE = SUPPORT_DIR / "support_tickets.json"

# ── Rule-based classification ─────────────────────────────────────────────────
# Checked in order — first match wins. More specific categories are listed first.

CATEGORY_KEYWORDS: dict = {
    "refund":       ["refund", "money back", "reimburs"],
    "cancellation": ["cancel", "cancellation", "unsubscribe", "terminate"],
    "billing":      ["billing", "invoice", "charge", "payment", "subscription", "plan"],
    "bug":          ["bug", "error", "crash", "broken", "not working", "issue", "fail"],
    "feature":      ["feature", "suggest", "request", "would love", "wish", "add support"],
    "support":      ["help", "support", "how to", "question", "stuck", "can't", "cannot"],
}

PRIORITY_HIGH = ["urgent", "asap", "critical", "emergency", "immediately", "blocking"]
PRIORITY_LOW  = ["question", "wondering", "curious", "whenever", "no rush", "fyi"]

SENTIMENT_POS = ["thank", "great", "love", "awesome", "amazing", "happy", "excellent"]
SENTIMENT_NEG = ["angry", "frustrated", "terrible", "worst", "awful", "disappointed", "useless", "hate"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _decode_str(value: str) -> str:
    """Decode RFC 2047 encoded email header value into plain text."""
    parts = decode_header(value or "")
    chunks = []
    for chunk, charset in parts:
        if isinstance(chunk, bytes):
            chunks.append(chunk.decode(charset or "utf-8", errors="replace"))
        else:
            chunks.append(chunk)
    return " ".join(chunks).strip()


def _extract_body(msg) -> str:
    """Pull plain-text body (first 500 chars) from a Message object."""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode("utf-8", errors="replace")[:500]
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode("utf-8", errors="replace")[:500]
    return ""


# ── Classification ────────────────────────────────────────────────────────────

def _classify_rule_based(text: str) -> Optional[str]:
    """Return a category on keyword match, else None (triggers Claude fallback)."""
    lower = text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in lower for kw in keywords):
            return category
    return None


def _classify_with_claude(subject: str, snippet: str) -> str:
    """
    Cheap Claude classification fallback — only called when no keyword matched.
    Uses Haiku (smallest/cheapest model) with a 10-token limit.
    """
    prompt = (
        "Classify this customer email into exactly one category.\n"
        "Categories: support, bug, billing, feature, refund, cancellation, other\n\n"
        f"Subject: {subject}\n"
        f"Body: {snippet[:400]}\n\n"
        "Reply with only the category word, nothing else."
    )
    try:
        result = run_agent_task(
            task=prompt,
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
        ).strip().lower()
        valid = {"support", "bug", "billing", "feature", "refund", "cancellation", "other"}
        return result if result in valid else "other"
    except Exception as e:
        logging.warning(f"Claude classification fallback failed: {e}")
        return "other"


def _get_priority(text: str) -> str:
    lower = text.lower()
    if any(kw in lower for kw in PRIORITY_HIGH):
        return "high"
    if any(kw in lower for kw in PRIORITY_LOW):
        return "low"
    return "medium"


def _get_sentiment(text: str) -> str:
    lower = text.lower()
    pos = sum(1 for kw in SENTIMENT_POS if kw in lower)
    neg = sum(1 for kw in SENTIMENT_NEG if kw in lower)
    if neg > pos:
        return "negative"
    if pos > neg:
        return "positive"
    return "neutral"


# ── Gmail IMAP fetch ──────────────────────────────────────────────────────────

def _fetch_emails(max_emails: int = 50) -> list:
    """
    Connect to Gmail IMAP (SSL, port 993) and return parsed Message objects.
    Fetches UNSEEN messages only — avoids reprocessing old history.
    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env.
    """
    address  = os.getenv("GMAIL_ADDRESS", "")
    password = os.getenv("GMAIL_APP_PASSWORD", "")

    if not address or not password:
        logging.error("GMAIL_ADDRESS or GMAIL_APP_PASSWORD not set — skipping fetch")
        return []

    messages = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993)
        mail.login(address, password)
        mail.select("INBOX")

        _, data = mail.search(None, "UNSEEN")
        ids = data[0].split() if data[0] else []
        ids = ids[-max_emails:]  # cap batch size

        for uid in ids:
            _, msg_data = mail.fetch(uid, "(RFC822)")
            raw = msg_data[0][1]
            messages.append(email.message_from_bytes(raw))

        mail.logout()
        logging.info(f"Fetched {len(messages)} unseen emails from Gmail")
    except Exception as e:
        logging.error(f"Gmail IMAP fetch failed: {e}")

    return messages


# ── Build ticket ──────────────────────────────────────────────────────────────

def _build_ticket(msg) -> dict:
    """Convert a parsed email Message into a structured support ticket dict."""
    msg_id    = msg.get("Message-ID", "").strip()
    thread_id = msg.get("In-Reply-To", "").strip() or msg_id
    subject   = _decode_str(msg.get("Subject", "(no subject)"))
    sender    = _decode_str(msg.get("From", ""))
    date      = msg.get("Date", "")
    snippet   = _extract_body(msg)

    combined = f"{subject} {snippet}"

    # Rule-based first; Claude only if nothing matched
    category = _classify_rule_based(combined)
    if category is None:
        category = _classify_with_claude(subject, snippet)

    return {
        "id":                       msg_id,
        "subject":                  subject,
        "sender":                   sender,
        "date":                     date,
        "category":                 category,
        "priority":                 _get_priority(combined),
        "sentiment":                _get_sentiment(combined),
        "summary":                  subject,        # subject is a safe zero-cost summary
        "raw_snippet":              snippet,
        "status":                   "open",
        "source_link_or_thread_id": thread_id,
        "triaged_at":               datetime.now().isoformat(),
    }


# ── Deduplicate & save ────────────────────────────────────────────────────────

def _load_seen_ids() -> set:
    """Return the set of all known ids and thread_ids from existing tickets."""
    existing = read_json(TICKETS_FILE)
    if not isinstance(existing, list):
        return set()
    seen = set()
    for t in existing:
        if t.get("id"):
            seen.add(t["id"])
        if t.get("source_link_or_thread_id"):
            seen.add(t["source_link_or_thread_id"])
    return seen


def _save_tickets(new_tickets: list) -> None:
    """Append new tickets to the existing JSON array on disk."""
    existing = read_json(TICKETS_FILE)
    if not isinstance(existing, list):
        existing = []
    existing.extend(new_tickets)
    write_json(TICKETS_FILE, existing)


# ── Public entry point ────────────────────────────────────────────────────────

def run_support_triage(max_emails: int = 50) -> dict:
    """
    Full triage run: fetch → classify → deduplicate → save.
    Returns a summary dict for the CLI runner to print.
    """
    logging.info("Starting support triage...")

    raw_messages = _fetch_emails(max_emails)
    if not raw_messages:
        logging.info("No emails fetched — nothing to triage.")
        return {"fetched": 0, "new": 0, "skipped": 0}

    seen_ids   = _load_seen_ids()
    new_tickets = []
    skipped    = 0

    for msg in raw_messages:
        ticket = _build_ticket(msg)
        # Deduplicate on both id and thread_id
        if ticket["id"] in seen_ids or ticket["source_link_or_thread_id"] in seen_ids:
            skipped += 1
            continue
        seen_ids.add(ticket["id"])
        seen_ids.add(ticket["source_link_or_thread_id"])
        new_tickets.append(ticket)

    if new_tickets:
        _save_tickets(new_tickets)
        logging.info(f"Saved {len(new_tickets)} new tickets → {TICKETS_FILE}")

    return {
        "fetched": len(raw_messages),
        "new":     len(new_tickets),
        "skipped": skipped,
    }
