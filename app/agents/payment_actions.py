from app.scheduler.notifier import send_telegram

def run_payment_success(record: dict) -> None:
    print(f"Payment success triggered: {record.get('id')}")

    from app.agents.customer_store import save_customer
    save_customer(record)

    # Link payment session to user account (safe: skips if no email or duplicate)
    try:
        from app.agents.user_linker import link_payment_to_user
        email = record.get("email") or record.get("customer_email", "")
        session_id = record.get("session_id", "")
        if email and session_id:
            linked = link_payment_to_user(session_id, email)
            print(f"User link: {'created/updated' if linked else 'already linked or skipped'} ({email})")
    except Exception:
        pass

    try:
        amount = record.get("amount", 0) / 100
        email = record.get("customer_email", "unknown")
        event_id = record.get("id", "")

        message = (
            f"New payment received:\n"
            f"Amount: €{amount:.2f}\n"
            f"Customer: {email}\n"
            f"Event ID: {event_id}"
        )

        send_telegram(message)

    except Exception:
        pass
