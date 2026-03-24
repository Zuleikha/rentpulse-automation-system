import requests
import logging
from app.utils.config import get_config

def post_buffer(content: str):
    cfg = get_config()
    token = cfg["BUFFER_ACCESS_TOKEN"]
    
    # Get all connected channel IDs
    profiles_url = "https://api.bufferapp.com/1/profiles.json"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(profiles_url, headers=headers)
    response.raise_for_status()
    profiles = response.json()
    
    # Post to all connected channels
    for profile in profiles:
        profile_id = profile["id"]
        post_url = "https://api.bufferapp.com/1/updates/create.json"
        payload = {
            "text": content,
            "profile_ids[]": profile_id,
            "now": True
        }
        result = requests.post(post_url, headers=headers, data=payload)
        result.raise_for_status()
        logging.info(f"Posted to Buffer channel: {profile['service']}")