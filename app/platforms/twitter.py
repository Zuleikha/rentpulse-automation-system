import tweepy
from app.utils.config import get_config

def post_twitter(content: str):
    cfg = get_config()
    client = tweepy.Client(
        consumer_key=cfg["TWITTER_API_KEY"],
        consumer_secret=cfg["TWITTER_API_SECRET"],
        access_token=cfg["TWITTER_ACCESS_TOKEN"],
        access_token_secret=cfg["TWITTER_ACCESS_SECRET"],
    )
    client.create_tweet(text=content)
