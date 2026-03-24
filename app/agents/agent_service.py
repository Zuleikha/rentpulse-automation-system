"""
OpenClaw-compatible agent service.

Runs structured Claude tasks and returns results.
Web search is enabled via the Anthropic web-search beta header.
"""
import json
import re
import anthropic
from app.utils.config import get_config


def run_agent_task(
    task: str,
    system: str = "",
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 4096,
    use_web_search: bool = False,
) -> str:
    """
    Run a single agent task via Claude and return the text response.

    When use_web_search=True, passes the Anthropic web-search beta header
    and registers the web_search tool so Claude can fetch live results.
    """
    cfg = get_config()
    client = anthropic.Anthropic(api_key=cfg["ANTHROPIC_API_KEY"])

    kwargs: dict = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": task}],
    }

    if system:
        kwargs["system"] = system

    if use_web_search:
        kwargs["tools"] = [{"type": "web_search_20250305", "name": "web_search"}]
        kwargs["extra_headers"] = {"anthropic-beta": "web-search-2025-03-05"}

    message = client.messages.create(**kwargs)

    # Collect all text blocks — web search responses interleave tool_use
    # blocks with text blocks; we want all the text in order.
    text_parts = [
        block.text
        for block in message.content
        if hasattr(block, "text")
    ]
    return "\n".join(text_parts).strip()


def extract_json(text: str):
    """
    Robustly extract the first JSON array or object from a string.

    Handles cases where Claude wraps JSON in markdown fences or adds
    prose before/after the JSON when using web search.
    """
    # Strip markdown fences
    text = re.sub(r"```(?:json)?", "", text).strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find outermost JSON array
    start = text.find("[")
    if start != -1:
        depth, end = 0, -1
        for i, ch in enumerate(text[start:], start):
            if ch == "[":
                depth += 1
            elif ch == "]":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

    # Find outermost JSON object
    start = text.find("{")
    if start != -1:
        depth, end = 0, -1
        for i, ch in enumerate(text[start:], start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass

    return []


# ---- OpenClaw-compatible aliases ----

def runAgentTask(*args, **kwargs) -> str:
    """Alias for run_agent_task — OpenClaw naming convention."""
    return run_agent_task(*args, **kwargs)


def run_research_agent(task: str, system: str = "", max_tokens: int = 4096,
                       use_web_search: bool = False) -> str:
    """Specialised alias for research tasks."""
    return run_agent_task(task=task, system=system, max_tokens=max_tokens,
                          use_web_search=use_web_search)
