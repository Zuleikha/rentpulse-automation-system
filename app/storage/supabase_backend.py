from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def save_payment(payment: dict) -> bool:
    session_id = payment.get("session_id", "")
    if session_id:
        existing = supabase.table("payments").select("session_id").eq("session_id", session_id).execute()
        if existing.data:
            return False
    supabase.table("payments").insert(payment).execute()
    return True


def get_payments() -> list:
    result = supabase.table("payments").select("*").execute()
    return result.data if result.data else []


def save_customer(customer: dict) -> bool:
    from datetime import datetime
    email = customer.get("email", "")
    if not email:
        return False
    existing = supabase.table("customers").select("email").eq("email", email).execute()
    if existing.data:
        return False
    entry = {
        "email":     email,
        "amount":    customer.get("amount", 0),
        "timestamp": customer.get("timestamp", datetime.utcnow().isoformat()),
    }
    supabase.table("customers").insert(entry).execute()
    return True


def get_customers() -> list:
    result = supabase.table("customers").select("*").execute()
    return result.data if result.data else []


def save_user(user: dict) -> bool:
    email = user.get("email", "")
    if not email:
        return False
    existing = supabase.table("users").select("email").eq("email", email).execute()
    if existing.data:
        return False
    supabase.table("users").insert(user).execute()
    return True


def get_users() -> list:
    result = supabase.table("users").select("*").execute()
    return result.data if result.data else []


def update_user(email: str, updates: dict) -> bool:
    if not email:
        return False
    existing = supabase.table("users").select("email").eq("email", email).execute()
    if not existing.data:
        return False
    supabase.table("users").update(updates).eq("email", email).execute()
    return True
