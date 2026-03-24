import anthropic
import json
import os
import logging
import time
from app.utils.config import get_config

RESEARCH_PROMPT = """
You are a social media strategist specialising in the Irish property market.
Research the best strategy for promoting RentPulse - a free Chrome extension 
that gives Irish renters instant property alerts.
Do not mention any specific property or rental websites by name in any output.
Return ONLY a JSON object with this exact structure, no other text:
{
  "twitter": {
    "best_times": ["08:00", "12:00", "18:00"],
    "hashtags": ["#IrishRental", "#DublinRent"],
    "tone": "punchy and direct"
  },
  "reddit": {
    "best_times": ["09:00", "13:00", "20:00"],
    "hashtags": [],
    "tone": "casual and helpful, like a real person",
    "subreddits": ["DublinRentals", "irishpersonalfinance", "ireland"]
  },
  "facebook": {
    "best_times": ["09:00", "13:00", "19:00"],
    "hashtags": ["#IrishRental", "#DublinHousing"],
    "tone": "friendly and conversational",
    "groups": ["Dublin Housing", "Accommodation Ireland"]
  },
  "linkedin": {
    "best_times": ["08:30", "12:00", "17:30"],
    "hashtags": ["#PropTech", "#IrishTech", "#RentalIreland"],
    "tone": "professional, builder sharing their product"
  }
}
"""

INSIGHTS_CACHE_FILE = "app/research/insights_cache.json"

def get_market_insights() -> dict:
    if os.path.exists(INSIGHTS_CACHE_FILE):
        with open(INSIGHTS_CACHE_FILE, "r") as f:
            cached = json.load(f)
            logging.info("Using cached market insights")
            return cached

    cfg = get_config()
    client = anthropic.Anthropic(api_key=cfg["ANTHROPIC_API_KEY"])

    for attempt in range(3):
        try:
            logging.info(f"Fetching market insights - attempt {attempt + 1}")
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=1200,
                messages=[{"role": "user", "content": RESEARCH_PROMPT}]
            )
            raw = message.content[0].text.strip()
            raw = raw.replace("```json", "").replace("```", "").strip()
            insights = json.loads(raw)
            with open(INSIGHTS_CACHE_FILE, "w") as f:
                json.dump(insights, f, indent=2)
            logging.info("Market insights cached successfully")
            return insights
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed: {e}")
            if attempt < 2:
                time.sleep(5)

    logging.error("All attempts failed - using default insights")
    return {
        "twitter": {"best_times": ["09:00", "13:00", "18:00"], "hashtags": ["#IrishRental", "#DublinRent"], "tone": "punchy and direct"},
        "reddit": {"best_times": ["09:00", "13:00", "20:00"], "hashtags": [], "tone": "casual and helpful"},
        "facebook": {"best_times": ["09:00", "13:00", "19:00"], "hashtags": ["#IrishRental"], "tone": "friendly"},
        "linkedin": {"best_times": ["08:30", "12:00", "17:30"], "hashtags": ["#PropTech", "#IrishTech"], "tone": "professional"}
    }

def get_platform_times(platform: str) -> list:
    insights = get_market_insights()
    return insights.get(platform, {}).get("best_times", ["09:00", "13:00", "18:00"])

def get_platform_hashtags(platform: str) -> list:
    insights = get_market_insights()
    return insights.get(platform, {}).get("hashtags", [])