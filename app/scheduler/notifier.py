import os
import logging
import time
import requests

TOKEN = lambda: os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = lambda: os.getenv("TELEGRAM_CHAT_ID")
BASE = lambda: f"https://api.telegram.org/bot{TOKEN()}"
TIMEOUT = int(os.getenv("APPROVAL_TIMEOUT_MINS", "30"))

def send_message(text: str, reply_markup=None) -> int:
    payload = {"chat_id": CHAT_ID(), "text": text, "parse_mode": "HTML"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = requests.post(f"{BASE()}/sendMessage", json=payload)
    return r.json().get("result", {}).get("message_id")

def edit_message(message_id: int, text: str):
    requests.post(f"{BASE()}/editMessageText", json={
        "chat_id": CHAT_ID(), "message_id": message_id,
        "text": text, "parse_mode": "HTML"
    })

def get_updates(offset: int = None):
    params = {"timeout": 10, "allowed_updates": ["callback_query", "message"]}
    if offset:
        params["offset"] = offset
    r = requests.get(f"{BASE()}/getUpdates", params=params)
    return r.json().get("result", [])

def answer_callback(callback_id: str):
    requests.post(f"{BASE()}/answerCallbackQuery", json={"callback_query_id": callback_id})

def flush_old_updates() -> int:
    """Discard any stale updates/callbacks so we don't auto-approve on restart."""
    updates = get_updates()
    if not updates:
        return None
    last_id = updates[-1]["update_id"] + 1
    get_updates(offset=last_id)  # marks all as read
    return last_id

def request_approval(platform: str, content: str) -> str:
    if not TOKEN() or not CHAT_ID():
        logging.warning("Telegram not configured - auto-approving")
        return content

    current_content = content
    last_update_id = flush_old_updates()  # clear stale callbacks before showing preview

    while True:
        preview = (
            f"<b>Review post for {platform.upper()}</b>\n\n"
            f"{current_content}\n\n"
            f"<i>Waiting {TIMEOUT} mins before auto-skip.</i>"
        )
        markup = {"inline_keyboard": [[
            {"text": "Approve", "callback_data": "approve"},
            {"text": "Edit",    "callback_data": "edit"},
            {"text": "Reject",  "callback_data": "reject"},
        ]]}
        msg_id = send_message(preview, reply_markup=markup)

        deadline = time.time() + (TIMEOUT * 60)

        while time.time() < deadline:
            updates = get_updates(offset=last_update_id)
            for update in updates:
                last_update_id = update["update_id"] + 1
                if "callback_query" in update:
                    cb = update["callback_query"]
                    answer_callback(cb["id"])
                    action = cb["data"]
                    if action == "approve":
                        edit_message(msg_id, f"<b>{platform.upper()}</b> - Approved. Posting now...")
                        return current_content
                    elif action == "reject":
                        edit_message(msg_id, f"<b>{platform.upper()}</b> - Rejected. Skipped.")
                        return None
                    elif action == "edit":
                        edit_message(msg_id, f"<b>{platform.upper()}</b> - Send me your edited version:")
                        edit_deadline = time.time() + 300
                        got_edit = False
                        while time.time() < edit_deadline:
                            edit_updates = get_updates(offset=last_update_id)
                            for eu in edit_updates:
                                last_update_id = eu["update_id"] + 1
                                if "message" in eu and "text" in eu["message"]:
                                    current_content = eu["message"]["text"]
                                    got_edit = True
                                    break
                            if got_edit:
                                break
                            time.sleep(2)
                        # Loop back to top - shows updated post with Approve/Edit/Reject buttons
                        break
            else:
                time.sleep(2)
                continue
            break  # break inner while to re-show updated post with buttons

        else:
            edit_message(msg_id, f"<b>{platform.upper()}</b> - Timed out. Skipped.")
            logging.warning(f"{platform} approval timed out")
            return None

def send_telegram(message: str):
    if not TOKEN() or not CHAT_ID():
        logging.warning("Telegram not configured")
        return
    send_message(message)