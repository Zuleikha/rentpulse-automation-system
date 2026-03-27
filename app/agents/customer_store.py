import json
from pathlib import Path
from datetime import datetime

CUSTOMERS_FILE = Path("data/customers/customers.json")

def save_customer(record: dict) -> None:
    try:
        email = record.get("customer_email", "")
        if not email:
            return

        CUSTOMERS_FILE.parent.mkdir(parents=True, exist_ok=True)

        if CUSTOMERS_FILE.exists():
            with open(CUSTOMERS_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        entry = {
            "email": email,
            "amount": record.get("amount", 0),
            "timestamp": datetime.utcnow().isoformat()
        }

        data.append(entry)

        with open(CUSTOMERS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    except Exception:
        pass
