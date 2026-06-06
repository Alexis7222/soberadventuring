import os
import json
import logging
from datetime import datetime
from pathlib import Path
import anthropic

from prompts.carousel_prompt import CAROUSEL_SYSTEM, CAROUSEL_USER_TEMPLATE
from prompts.reel_prompt import REEL_SYSTEM, REEL_USER_TEMPLATE
from prompts.monthly_prompt import MONTHLY_SYSTEM, MONTHLY_USER_TEMPLATE

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")
MODEL = "claude-sonnet-4-6"


def _build_trend_summary(research: dict) -> str:
    hooks = research.get("top_hooks", [])
    posts = research.get("top_posts", [])
    lines = ["Top performing hooks this week (by engagement rate):"]
    for i, hook in enumerate(hooks[:5], 1):
        lines.append(f"{i}. {hook}")
    if posts:
        top_ers = [p["engagement_rate"] for p in posts[:3]]
        lines.append(f"\nTop engagement rates: {top_ers}%")
    lines.append(f"Total posts analyzed: {research.get('total_analyzed', 0)}")
    lines.append(f"Source: {research.get('scraped_at', 'unknown')}")
    return "\n".join(lines)


def _call_claude(system: str, user: str) -> list | dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    raw = msg.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    if raw.lower().startswith("json"):
        raw = raw[4:]
    return json.loads(raw.strip())


def generate_carousels(week_date: str, trend_summary: str) -> list:
    user = CAROUSEL_USER_TEMPLATE.format(week_date=week_date, trend_summary=trend_summary)
    return _call_claude(CAROUSEL_SYSTEM, user)


def generate_reels(week_date: str, trend_summary: str) -> list:
    user = REEL_USER_TEMPLATE.format(week_date=week_date, trend_summary=trend_summary)
    return _call_claude(REEL_SYSTEM, user)


def generate_monthly(month_year: str) -> dict:
    angle = "How the same failures that defined the addiction years built the entrepreneur"
    user = MONTHLY_USER_TEMPLATE.format(month_year=month_year, monthly_angle=angle)
    return _call_claude(MONTHLY_SYSTEM, user)


def generate_content(research: dict, week_date: str) -> dict:
    trend_summary = _build_trend_summary(research)

    print("  Generating carousels...")
    carousels = generate_carousels(week_date, trend_summary)

    print("  Generating reels...")
    reels = generate_reels(week_date, trend_summary)

    monthly = None
    today = datetime.today()
    if today.day <= 7:
        print("  Generating monthly long-form...")
        monthly = generate_monthly(today.strftime("%B %Y"))

    return {
        "week_date": week_date,
        "trend_summary": trend_summary,
        "carousels": carousels,
        "reels": reels,
        "monthly": monthly,
    }
