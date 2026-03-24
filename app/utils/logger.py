import logging
import os

def setup_logger():
    log_dir = "/app/logs"
    os.makedirs(log_dir, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{log_dir}/bot.log"),
            logging.StreamHandler(),
        ]
    )
    return logging.getLogger("rentpulse-bot")

logger = setup_logger()
