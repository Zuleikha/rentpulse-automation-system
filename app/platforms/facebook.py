# Facebook posting - requires Meta Graph API
# Add FACEBOOK_PAGE_ID and FACEBOOK_ACCESS_TOKEN to .env when ready
import requests
import os

def post_facebook(content: str):
    page_id = os.getenv("FACEBOOK_PAGE_ID")
    token = os.getenv("FACEBOOK_ACCESS_TOKEN")
    if not page_id or not token:
        raise EnvironmentError("Facebook credentials not configured")
    url = f"https://graph.facebook.com/{page_id}/feed"
    response = requests.post(url, data={"message": content, "access_token": token})
    response.raise_for_status()
