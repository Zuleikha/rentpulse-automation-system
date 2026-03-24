import json
from pathlib import Path
from typing import List, Optional

import anthropic

from app.content.prompts import build_prompt_for_platform
from app.utils.config import get_config


RECENT_POSTS_DIR = Path("data/recent_posts")
MAX_RECENT_POSTS = 20


def _get_recent_posts_file(platform: str) -> Path:
    RECENT_POSTS_DIR.mkdir(parents=True, exist_ok=True)
    safe_platform = platform.strip().lower()
    return RECENT_POSTS_DIR / f"{safe_platform}_recent_posts.json"


def load_recent_posts(platform: str) -> List[str]:
    file_path = _get_recent_posts_file(platform)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return [str(item).strip() for item in data if str(item).strip()]

        return []
    except (json.JSONDecodeError, OSError):
        return []


def save_recent_post(platform: str, post: str) -> None:
    if not post or not post.strip():
        return

    existing_posts = load_recent_posts(platform)
    existing_posts.append(post.strip())

    trimmed_posts = existing_posts[-MAX_RECENT_POSTS:]
    file_path = _get_recent_posts_file(platform)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(trimmed_posts, f, ensure_ascii=False, indent=2)


def generate_post(platform: str, recent_posts: Optional[List[str]] = None) -> str:
    cfg = get_config()
    client = anthropic.Anthropic(api_key=cfg["ANTHROPIC_API_KEY"])

    posts_for_context = recent_posts if recent_posts is not None else load_recent_posts(platform)

    prompt = build_prompt_for_platform(
        platform=platform,
        recent_posts=posts_for_context,
        use_topic_pool=True,
        use_hashtag_pool=True,
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )

    post = message.content[0].text.strip()
    save_recent_post(platform, post)
    return post