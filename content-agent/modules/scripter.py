import os
import re
import json
import logging
from datetime import datetime
from pathlib import Path
import anthropic

from prompts.carousel_prompt import (
    CAROUSEL_SYSTEM,
    CAROUSEL_USER_TEMPLATE,
    CAROUSEL_CALENDAR_SECTION,
    CAROUSEL_FREEFORM_SECTION,
)
from prompts.reel_prompt import (
    REEL_SYSTEM,
    REEL_USER_TEMPLATE,
    REEL_CALENDAR_SECTION,
    REEL_FREEFORM_SECTION,
)
from prompts.stories_prompt import STORIES_SYSTEM, STORIES_USER_TEMPLATE
from prompts.monthly_prompt import MONTHLY_SYSTEM, MONTHLY_USER_TEMPLATE
from modules.notion_reader import fetch_this_weeks_calendar_topics, fetch_this_weeks_tiktok_topics

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")
MODEL = "claude-sonnet-4-6"
VAULT_ALERT_THRESHOLD = 300


def _build_trend_summary(research: dict) -> str:
    hooks = research.get("top_hooks", [])
    posts = research.get("top_posts", [])
    lines = ["Top performing hooks this week in the niche (by engagement rate):"]
    for i, hook in enumerate(hooks[:5], 1):
        lines.append(f"{i}. {hook}")
    if posts:
        top_ers = [p["engagement_rate"] for p in posts[:3]]
        lines.append(f"\nTop engagement rates in niche: {top_ers}%")
    lines.append(f"Total posts analyzed: {research.get('total_analyzed', 0)}")
    lines.append(f"Source: {research.get('scraped_at', 'unknown')}")
    return "\n".join(lines)


def _build_own_posts_summary(research: dict) -> str:
    own_posts = research.get("own_top_posts", [])
    if not own_posts:
        return "No own post data available this week — use character brief analytics."
    lines = ["@soberadventuring TOP PERFORMING POSTS (ranked by likes):"]
    for i, p in enumerate(own_posts[:10], 1):
        lines.append(
            f"{i}. [{p.get('type', '?').upper()}] {p.get('likes', 0)} likes, {p.get('comments', 0)} comments | "
            f"ER: {p.get('engagement_rate', 0)}%\n"
            f"   Hook: {p.get('hook', '')[:120]}"
        )
    return "\n".join(lines)


def _build_calendar_section(topics: list, calendar_template: str, freeform_section: str) -> str:
    if not topics:
        return freeform_section
    topic_lines = []
    for i, t in enumerate(topics, 1):
        draft_excerpt = (t.get("draft", "") or "")[:200]
        lines = [
            f"{i}. \"{t['title']}\" | {t.get('content_type', '')} | Pillar: {t.get('pillar', '')}",
            f"   Date: {t.get('date', '')} | Feeds: {t.get('feeds_offer', '')}",
        ]
        if draft_excerpt:
            lines.append(f"   Seed draft: {draft_excerpt}")
        topic_lines.append("\n".join(lines))
    return calendar_template.format(
        topic_list="\n\n".join(topic_lines),
        count=len(topics),
    )


def _detect_vault_alerts(research: dict) -> list:
    """Flag own posts exceeding the threshold that aren't already in the gold vault."""
    try:
        from prompts.gold_vault import GOLD_POSTS
        vault_hooks = [p["title"].lower() for p in GOLD_POSTS]
    except Exception:
        return []

    alerts = []
    for p in research.get("own_top_posts", []):
        likes = p.get("likes", 0)
        if likes >= VAULT_ALERT_THRESHOLD:
            hook = (p.get("hook", "") or "")[:100]
            hook_lower = hook.lower()
            already_in_vault = any(
                hook_lower[:40] in title or title[:40] in hook_lower
                for title in vault_hooks
            )
            if not already_in_vault and hook:
                alerts.append({
                    "hook": hook,
                    "likes": likes,
                    "comments": p.get("comments", 0),
                })
    return alerts


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
    raw = re.sub(r',\s*([}\]])', r'\1', raw.strip())
    return json.loads(raw)


def generate_carousels(week_date: str, trend_summary: str, own_posts_summary: str, calendar_topics: list) -> list:
    calendar_section = _build_calendar_section(calendar_topics, CAROUSEL_CALENDAR_SECTION, CAROUSEL_FREEFORM_SECTION)
    user = CAROUSEL_USER_TEMPLATE.format(
        week_date=week_date,
        calendar_section=calendar_section,
        trend_summary=trend_summary,
        own_posts_summary=own_posts_summary,
    )
    return _call_claude(CAROUSEL_SYSTEM, user)


def generate_reels(week_date: str, trend_summary: str, own_posts_summary: str, tiktok_topics: list) -> list:
    calendar_section = _build_calendar_section(tiktok_topics, REEL_CALENDAR_SECTION, REEL_FREEFORM_SECTION)
    user = REEL_USER_TEMPLATE.format(
        week_date=week_date,
        calendar_section=calendar_section,
        trend_summary=trend_summary,
        own_posts_summary=own_posts_summary,
    )
    return _call_claude(REEL_SYSTEM, user)


def generate_stories(week_date: str, own_posts_summary: str) -> list:
    user = STORIES_USER_TEMPLATE.format(
        week_date=week_date,
        own_posts_summary=own_posts_summary,
    )
    return _call_claude(STORIES_SYSTEM, user)


def generate_monthly(month_year: str) -> dict:
    angle = "How the same failures that defined the addiction years built the entrepreneur"
    user = MONTHLY_USER_TEMPLATE.format(month_year=month_year, monthly_angle=angle)
    return _call_claude(MONTHLY_SYSTEM, user)


def generate_content(research: dict, week_date: str) -> dict:
    trend_summary = _build_trend_summary(research)
    own_posts_summary = _build_own_posts_summary(research)

    print("  Reading Notion content calendar for this week's topics...")
    calendar_topics = fetch_this_weeks_calendar_topics()
    tiktok_topics = fetch_this_weeks_tiktok_topics()
    if calendar_topics:
        print(f"  Scripting {len(calendar_topics)} calendar-planned Instagram topics")
    else:
        print("  No Instagram calendar topics — generating 6 original carousel concepts")
    if tiktok_topics:
        print(f"  Scripting {len(tiktok_topics)} calendar-planned TikTok topics")
    else:
        print("  No TikTok calendar topics — generating 4 original reel concepts")

    print("  Checking for new high performers to add to gold vault...")
    vault_alerts = _detect_vault_alerts(research)
    if vault_alerts:
        print(f"  Gold vault alert: {len(vault_alerts)} post(s) above {VAULT_ALERT_THRESHOLD} likes not in vault")

    print("  Generating carousels...")
    carousels = generate_carousels(week_date, trend_summary, own_posts_summary, calendar_topics)

    print("  Generating reels...")
    reels = generate_reels(week_date, trend_summary, own_posts_summary, tiktok_topics)

    print("  Generating stories...")
    stories = generate_stories(week_date, own_posts_summary)

    monthly = None
    today = datetime.today()
    if today.day <= 7:
        print("  Generating monthly long-form...")
        monthly = generate_monthly(today.strftime("%B %Y"))

    return {
        "week_date": week_date,
        "calendar_topics_count": len(calendar_topics),
        "tiktok_topics_count": len(tiktok_topics),
        "trend_summary": trend_summary,
        "own_posts_summary": own_posts_summary,
        "carousels": carousels,
        "reels": reels,
        "stories": stories,
        "vault_alerts": vault_alerts,
        "monthly": monthly,
    }
