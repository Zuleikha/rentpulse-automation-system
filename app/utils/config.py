import os
from dotenv import load_dotenv
load_dotenv()

REQUIRED_KEYS = [
    "ANTHROPIC_API_KEY",
    "TELEGRAM_BOT_TOKEN",
    "TELEGRAM_CHAT_ID",
    "BLUESKY_HANDLE",
    "BLUESKY_APP_PASSWORD",
]

def get_config() -> dict:
    missing = [k for k in REQUIRED_KEYS if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing required env vars: {', '.join(missing)}")
    return {k: os.getenv(k) for k in os.environ}