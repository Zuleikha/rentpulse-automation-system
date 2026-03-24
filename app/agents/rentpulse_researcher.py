"""
RentPulse Research agent.

Uses Claude with live web search to find real signals about:
- People actively looking for rentals in Ireland
- Real complaints renters are posting online
- Competitor tools people actually use
- Content ideas grounded in current conversations

All results saved locally to data/rentpulse/ — no external DB.
"""
import logging
from datetime import datetime

from app.agents.agent_service import run_agent_task, extract_json
from app.utils.local_storage import RENTPULSE_DIR, write_json

RENTPULSE_SYSTEM = """You are a product researcher for RentPulse, a Chrome extension
that sends instant desktop alerts for new Irish rental listings across multiple rental sites.

Your job is to find REAL, current signals from the internet — actual posts, threads,
complaints, tools, and conversations — not hypothetical examples.

Rules:
- Only report things you actually found via web search
- Do not invent quotes, posts, or signals
- Do not name specific rental property listing sites directly
- Be specific: include platform, post context, and timeframe when available
- Return valid JSON arrays only — no markdown, no preamble, no trailing text
"""

RESEARCH_TASKS = {
    "leads": {
        "prompt": """
Use web search to find REAL posts and threads from people in Ireland who are
actively trying to find rental accommodation right now.

Search these sources:
- reddit.com/r/ireland — search "renting", "looking for place", "accommodation",
  "lease", "room to rent dublin"
- reddit.com/r/dublin — search "accommodation", "looking for flat", "renting",
  "rental alert", "missed a listing"
- reddit.com/r/DublinHousing — search recent posts about looking for housing
- reddit.com/r/irishpersonalfinance — search "renting", "rental costs"
- boards.ie — search "accommodation wanted", "house hunting ireland"
- Twitter/X — search "looking for rent ireland", "dublin rent", "missed listing"

For each REAL signal you find, extract:
- What the person said or asked
- Where you found it (subreddit, site, etc)
- How urgently they seemed to need housing
- The location they want

Return ONLY a JSON array:
[
  {
    "source": "reddit r/dublin / boards.ie / twitter etc",
    "signal": "what the person actually said or asked — quote or close paraphrase",
    "location": "Dublin / Cork / Galway / Ireland general / unknown",
    "urgency": "high or medium or low",
    "angle": "how RentPulse instant alerts would directly help this specific person"
  }
]

Only return entries based on real posts you found. Do not invent signals.
Return up to 15 results.
""",
        "file": "leads.json",
    },

    "complaints": {
        "prompt": """
Use web search to find REAL complaints and frustrations that Irish renters are
posting online right now or in the last few weeks.

Search these sources:
- reddit.com/r/ireland and r/dublin — search "missed listing", "too late", "refreshing",
  "competition for rental", "applied too slow", "gone before I could apply",
  "rental nightmare", "housing stress ireland"
- reddit.com/r/DublinHousing — browse recent posts
- boards.ie accommodation section
- Twitter/X — search "ireland rent", "dublin rent frustration", "missed listing ireland"
- Google — search 'ireland renters "missed it" OR "gone already" OR "too slow" site:reddit.com'

For each REAL complaint found:

Return ONLY a JSON array:
[
  {
    "platform": "reddit r/ireland / twitter / boards.ie etc",
    "complaint": "what the person actually said — direct quote or close paraphrase",
    "theme": "core frustration in 3-5 words",
    "frequency": "very common / common / occasional — based on how many similar posts you found",
    "content_opportunity": "type of RentPulse post that would resonate with this frustration"
  }
]

Only return entries based on real posts you found. Do not fabricate complaints.
Return up to 12 results.
""",
        "file": "complaints.json",
    },

    "competitors": {
        "prompt": """
Use web search to find REAL tools, apps, bots, and services that Irish renters
currently use to find rental listings faster or get alerts.

Search for:
- "rental alerts ireland" — tools, sites, apps offering this
- "daft.ie alerts" OR "myhome.ie alerts" — browser extensions or scripts
- "ireland rental bot telegram" — Telegram bots for rental alerts
- "rental notifications ireland app"
- Reddit threads where Irish renters share tips on how to be first to listings
- GitHub — search "ireland rental alert", "daft scraper", "rental bot ireland"
- Chrome Web Store — search "ireland rent alert", "rental notifications"
- Google — "best way to get rental alerts ireland 2024 2025"

For each REAL tool you find:

Return ONLY a JSON array:
[
  {
    "name": "exact name of the tool or service",
    "type": "extension or app or bot or service or site or script",
    "what_it_does": "what it actually does based on what you found",
    "strengths": "what it does well based on user feedback or feature description",
    "weaknesses": "limitations mentioned by users or gaps you observed",
    "rentpulse_advantage": "how RentPulse differs or could do better for Irish renters"
  }
]

Only list tools you actually found evidence of. Do not invent competitors.
Return up to 10 results.
""",
        "file": "competitors.json",
    },

    "content_ideas": {
        "prompt": """
Use web search to find what Irish renters are actually talking about online
right now, then generate content post ideas for RentPulse based on those
REAL current conversations.

First search for:
- Recent Reddit threads in r/ireland, r/dublin, r/DublinHousing about renting
- Recent Irish news about rental market (irishtimes.com, thejournal.ie, rte.ie)
- Twitter/X posts about renting in Ireland this week
- Any viral or highly-upvoted posts about Irish housing stress

Then create content ideas that are grounded in what you actually found — not generic ideas.

Return ONLY a JSON array:
[
  {
    "idea": "specific post concept tied to a real conversation or news item you found",
    "platform": "Twitter/X or Reddit or Bluesky or Facebook or Threads or LinkedIn or Instagram",
    "angle": "one of: speed_of_listings / rental_competition / renters_refreshing_pages / missing_listings_by_minutes / timing_matters_in_renting / small_tools_that_help_renters",
    "hook": "opening line that feels native and human — not promotional",
    "why_now": "the real source or conversation you found that makes this timely",
    "estimated_engagement": "high or medium or low"
  }
]

Return 10 to 15 ideas grounded in what you actually found.
""",
        "file": "content_ideas.json",
    },
}


def run_research_task(task_name: str) -> list:
    """Run a single named research task with live web search and save results."""
    task = RESEARCH_TASKS.get(task_name)
    if not task:
        logging.error(f"Unknown research task: {task_name}")
        return []

    logging.info(f"Running research task: {task_name} (live web search)")

    results = []
    try:
        response = run_agent_task(
            task=task["prompt"],
            system=RENTPULSE_SYSTEM,
            model="claude-sonnet-4-6",
            max_tokens=8000,
            use_web_search=True,
        )

        parsed = extract_json(response)

        if isinstance(parsed, list):
            results = [r for r in parsed if isinstance(r, dict) and r]
        elif isinstance(parsed, dict):
            # Some tasks might wrap the array in a key
            for v in parsed.values():
                if isinstance(v, list):
                    results = v
                    break

    except Exception as e:
        logging.error(f"Research task '{task_name}' failed: {e}")
        results = []

    ts = datetime.now().isoformat()
    for item in results:
        item["researched_at"] = ts

    write_json(RENTPULSE_DIR / task["file"], results)
    logging.info(f"Task '{task_name}' complete: {len(results)} results saved")
    return results


def run_all_research() -> dict:
    """Run all RentPulse research tasks and return a summary dict."""
    results = {}
    for task_name in RESEARCH_TASKS:
        results[task_name] = run_research_task(task_name)
        logging.info(f"Completed: {task_name} ({len(results[task_name])} items)")
    return results
