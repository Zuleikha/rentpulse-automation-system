import random
from typing import List, Optional


POST_ANGLES = [
    "speed_of_listings",
    "rental_competition",
    "renters_refreshing_pages",
    "missing_listings_by_minutes",
    "timing_matters_in_renting",
    "small_tools_that_help_renters",
    "observing_the_rental_market",
    "trying_to_be_first_to_apply",
    "renting_feels_like_a_second_job",
    "builder_solving_a_small_problem",
]

POST_HOOKS = [
    "Most rental listings are gone before people even see them.",
    "Renting in Ireland has become a timing game.",
    "Missing a listing by 10 minutes can mean missing it completely.",
    "For a lot of renters, checking listings has become a second job.",
    "The hardest part of renting is often just seeing a place in time.",
    "A good rental can disappear faster than most people can react.",
    "In renting, speed matters more than ever.",
    "A lot of renters are not too late because they are careless. They are too late because the process is broken.",
    "The window to catch a decent rental is often tiny.",
    "The difference between seeing a listing early and late is everything.",
]

SOFT_CTA_STYLES = [
    "mention_the_tool_casually",
    "end_with_a_quiet_recommendation",
    "frame_it_as_something_helpful_you_built",
    "mention_it_like_a_useful_tip",
    "refer_to_it_as_a_small_tool_not_a_product",
]

AVOID_PHRASES = [
    "game changer",
    "check it out",
    "sign up now",
    "do not miss out",
    "perfect for renters",
    "revolutionising renting",
    "super useful",
    "must-have tool",
    "free chrome extension for renters",
    "built to help renters",
]

TOPIC_POOL = [
    "renters missing listings by minutes",
    "good rentals disappearing too fast",
    "refreshing pages constantly to catch something early",
    "timing matters more than ever in renting",
    "renting feels like a second job",
    "competition for rental listings is intense",
    "being early is often the only advantage renters have",
]

HASHTAG_POOLS = {
    "linkedin": [
        "#Ireland",
        "#Housing",
        "#HousingCrisis",
        "#PropTech",
        "#BuildInPublic",
        "#Startups",
        "#TechForGood"
    ],
    "twitter": [
        "#RentingIreland",
        "#HousingIreland",
        "#DublinRent",
        "#IrishHousing",
        "#RentalMarket",
        "#HousingCrisis"
    ],
    "bluesky": [
        "#RentingIreland",
        "#HousingIreland",
        "#IrishHousing",
        "#DublinRent"
    ],
    "facebook": [
        "#RentingIreland",
        "#IrishHousing",
        "#DublinRent"
    ],
    "reddit": []
}


def get_post_angle() -> str:
    return random.choice(POST_ANGLES)


def get_post_hook() -> str:
    return random.choice(POST_HOOKS)


def get_soft_cta_style() -> str:
    return random.choice(SOFT_CTA_STYLES)


def get_topic() -> str:
    return random.choice(TOPIC_POOL)


def get_platform_hashtags(platform: str, max_tags: int = 2) -> List[str]:
    tags = HASHTAG_POOLS.get(platform, [])
    if not tags:
        return []
    sample_size = min(max_tags, len(tags))
    return random.sample(tags, sample_size)


def build_recent_posts_instruction(recent_posts: Optional[List[str]] = None) -> str:
    if not recent_posts:
        return ""

    cleaned_posts = [post.strip() for post in recent_posts if post and post.strip()]
    if not cleaned_posts:
        return ""

    recent_text = " || ".join(cleaned_posts[-20:])

    return (
        "Avoid repeating ideas, hooks, phrasing, or sentence structure from these recent posts: "
        f"{recent_text}. "
    )


def build_avoid_phrases_instruction() -> str:
    phrases = ", ".join(f"'{phrase}'" for phrase in AVOID_PHRASES)
    return f"Do not use these phrases: {phrases}. "


def get_platform_prompt(
    platform: str,
    hashtags: Optional[List[str]] = None,
    topic: str = "",
    recent_posts: Optional[List[str]] = None,
) -> str:
    hashtag_str = " ".join(hashtags) if hashtags else ""
    angle = get_post_angle()
    hook = get_post_hook()
    cta_style = get_soft_cta_style()

    topic_context = (
        f"Use this renter discussion as background context: '{topic}'. "
        f"Do not say it came from another platform. "
        if topic else ""
    )

    recent_posts_instruction = build_recent_posts_instruction(recent_posts)
    avoid_phrases_instruction = build_avoid_phrases_instruction()

    common_rules = (
        f"{topic_context}"
        f"{recent_posts_instruction}"
        f"{avoid_phrases_instruction}"
        f"Focus on this angle: {angle}. "
        f"Use this opening idea or something close to it as the first line: '{hook}'. "
        f"End with a natural observation or question instead of promoting a tool. "
        f"Only mention RentPulse if it fits naturally. "
        f"Sometimes write the post without mentioning it. "
        f"If mentioned, refer to it casually as something you tried while renting. "
        f"Do not sound like advertising. "
        f"No emojis. No hype. No sales language. "
        f"No mention of specific rental sites. "
        f"Write like a real person. "
        f"Prefer sounding like a renter sharing an observation rather than recommending a tool. "
        f"Vary wording, rhythm, and sentence openings. "
        f"Avoid generic AI-sounding phrases. "
        f"Avoid repeating the word 'Ireland' too often in short posts. "
    )

    prompts = {
        "bluesky": (
            f"{topic_context}"
            f"Write one Bluesky post about renting in Ireland. "
            f"The final post MUST be under 170 characters. "
            f"If the draft is longer, shorten it before returning. "
            f"Prefer 120–160 characters when possible. "
            f"Never produce a thread. Only one post. "
            f"Use a natural conversational tone. "
            f"Do not sound like advertising. "
            f"No emojis. No hype. No sales language. "
            f"No mention of specific rental sites. "
            f"Write like a real renter observation. "
            f"Focus on this angle: {angle}. "
            f"Use this opening idea or something close to it: '{hook}'. "
            f"Mention RentPulse naturally as a small Chrome extension that alerts when new rentals appear. "
            f"Prefer 2–3 short lines instead of a long paragraph. "
            f"Keep wording simple and human. "
            f"Include hashtags only if they fit naturally: {hashtag_str}."
        ),
        "twitter": (
            f"{common_rules}"
            f"Write a short X post about renting in Ireland. "
            f"Tone: punchy, direct, natural. "
            f"Keep it tight. Prefer 140-190 characters when possible. "
            f"Include hashtags only if natural: {hashtag_str}."
        ),
        "reddit": (
            f"{common_rules}"
            f"Write a short Reddit-style post about renting in Ireland. "
            f"Write like a real renter sharing an observation or tip. "
            f"Mention RentPulse only near the end. "
            f"Tone: honest, conversational, grounded. "
            f"Max 120 words."
        ),
        "linkedin": (
            f"{common_rules}"
            f"Write a short LinkedIn post from the perspective of a builder solving a real problem in Ireland. "
            f"Explain that timing matters when new rental listings appear. "
            f"Tone: thoughtful, credible, builder-focused, professional. "
            f"Max 140 words. "
            f"Hashtags are optional. Only include them if they fit naturally: {hashtag_str}."
        ),
        "facebook": (
            f"{common_rules}"
            f"Write a short Facebook post about the reality of renting in Ireland. "
            f"Make it relatable to renters in Dublin, Cork or Galway. "
            f"Tone: informal, community discussion, useful. "
            f"Max 100 words. "
            f"Include hashtags only if natural: {hashtag_str}."
        ),
    }

    return prompts.get(
        platform,
        (
            f"{common_rules}"
            "Write a natural post about renting in Ireland and briefly mention RentPulse without sounding promotional."
        ),
    )


def build_prompt_for_platform(
    platform: str,
    recent_posts: Optional[List[str]] = None,
    use_topic_pool: bool = True,
    use_hashtag_pool: bool = True,
) -> str:
    topic = get_topic() if use_topic_pool else ""
    hashtags = get_platform_hashtags(platform) if use_hashtag_pool else []
    return get_platform_prompt(
        platform=platform,
        hashtags=hashtags,
        topic=topic,
        recent_posts=recent_posts,
    )


MARKET_RESEARCH_PROMPT = """
Research how people in Ireland talk online about renting, housing stress, missing listings,
competition for properties, and the difficulty of being early enough to apply.

Return:
1. Common phrases real renters use
2. Common frustrations
3. Common discussion themes
4. Tone patterns by platform:
   - Reddit
   - X
   - Bluesky
   - Facebook
   - LinkedIn
5. Post ideas that feel native and not promotional

Rules:
- Focus on Ireland
- No mention of specific rental sites
- Prefer natural renter language over marketing language
- Highlight wording that sounds human and wording that sounds like an ad
""".strip()