import schedule
import time
import os
from dotenv import load_dotenv
from app.content.generator import generate_post
from app.platforms.bluesky import post_bluesky
from app.scheduler.notifier import send_telegram, request_approval
from app.utils.logger import logger
load_dotenv()


def run_posts():
    results = []
    try:
        content = generate_post("bluesky")
        approved_content = request_approval("bluesky", content)
        if approved_content is None:
            results.append("bluesky: skipped")
        else:
            post_bluesky(approved_content)
            results.append("bluesky: posted")
            logger.info("Posted to Bluesky")
    except Exception as e:
        results.append(f"bluesky: FAILED - {e}")
        logger.error(f"Bluesky post failed: {e}")
    send_telegram("RentPulse Bot Update:\n" + "\n".join(results))

def main():
    run_posts()  # run immediately on start
    times = os.getenv("POST_TIMES", "09:00,13:00,18:00").split(",")
    for t in times:
        schedule.every().day.at(t.strip()).do(run_posts)
    logger.info("RentPulse social bot started")
    send_telegram("RentPulse Bot started and running.")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()