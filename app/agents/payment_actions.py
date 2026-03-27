from app.scheduler.notifier import send_telegram

def run_payment_success(record: dict) -> None:
    print(f"Payment success triggered: {record.get('id')}")
    from app.agents.customer_store import save_customer
    save_customer(record)
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
