import requests
import logging
from datetime import datetime, timezone
from app.utils.config import get_config

def post_bluesky(content: str):
    cfg = get_config()
    handle = cfg["BLUESKY_HANDLE"]
    password = cfg["BLUESKY_APP_PASSWORD"]

    # Login to get access token
    auth_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}
    )
    auth_response.raise_for_status()
    token = auth_response.json()["accessJwt"]

    # Post to Bluesky
    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "repo": handle,
            "collection": "app.bsky.feed.post",
            "record": {
                "text": content,
                "$type": "app.bsky.feed.post",
                "createdAt": datetime.now(timezone.utc).isoformat()
            }
        }
    )
    response.raise_for_status()
    logging.info("Posted to Bluesky successfully")