import praw
from app.utils.config import get_config

def post_reddit(content: str):
    cfg = get_config()
    reddit = praw.Reddit(
        client_id=cfg["REDDIT_CLIENT_ID"],
        client_secret=cfg["REDDIT_CLIENT_SECRET"],
        username=cfg["REDDIT_USERNAME"],
        password=cfg["REDDIT_PASSWORD"],
        user_agent="RentPulse Bot/1.0",
    )
    subreddit = reddit.subreddit("DublinRentals")
    subreddit.submit(title="Found a tool that helped me with Daft.ie alerts", selftext=content)
