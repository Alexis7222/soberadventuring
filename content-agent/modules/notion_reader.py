import os
import requests
from datetime import datetime, timedelta

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

NOTION_BASE_URL = "https://api.notion.com/v1"


def _get_prop(props: dict, name: str) -> str:
    prop = props.get(name, {})
    ptype = prop.get("type", "")
    if ptype == "rich_text":
        texts = prop.get("rich_text", [])
        return texts[0]["text"]["content"] if texts else ""
    if ptype == "title":
        texts = prop.get("title", [])
        return texts[0]["text"]["content"] if texts else ""
    if ptype == "select":
        sel = prop.get("select")
        return sel["name"] if sel else ""
    if ptype == "date":
        d = prop.get("date")
        return d["start"] if d else ""
    return ""


def _next_week_range() -> tuple:
    today = datetime.today()
    days_to_next_monday = (7 - today.weekday()) % 7
    if days_to_next_monday == 0:
        days_to_next_monday = 7
    next_monday = today + timedelta(days=days_to_next_monday)
    following_monday = next_monday + timedelta(days=7)
    return next_monday, following_monday


def _fetch_calendar_topics(platform: str) -> list:
    if not NOTION_DATABASE_ID or not NOTION_API_KEY:
        print(f"  Notion calendar unavailable — NOTION_DATABASE_ID or NOTION_API_KEY not set")
        return []

    next_monday, following_monday = _next_week_range()

    url = f"{NOTION_BASE_URL}/databases/{NOTION_DATABASE_ID}/query"
    payload = {
        "filter": {
            "and": [
                {"property": "Platform", "select": {"equals": platform}},
                {"property": "Date", "date": {"on_or_after": next_monday.strftime("%Y-%m-%d")}},
                {"property": "Date", "date": {"before": following_monday.strftime("%Y-%m-%d")}},
            ]
        },
        "sorts": [{"property": "Date", "direction": "ascending"}],
    }

    try:
        resp = requests.post(url, headers=NOTION_HEADERS, json=payload, timeout=15)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        topics = []
        for page in results:
            props = page.get("properties", {})
            topics.append({
                "title": _get_prop(props, "Title"),
                "date": _get_prop(props, "Date"),
                "content_type": _get_prop(props, "Content Type"),
                "pillar": _get_prop(props, "Pillar"),
                "feeds_offer": _get_prop(props, "Feeds Offer"),
                "draft": _get_prop(props, "Hook / Caption Draft"),
                "target_keyword": _get_prop(props, "Target Keyword"),
            })
        print(f"  Notion calendar: {len(topics)} {platform} topics found for week of {next_monday.strftime('%B %d')}")
        return topics
    except Exception as exc:
        print(f"  Notion {platform} calendar read failed: {exc} — will generate original topics")
        return []


def fetch_this_weeks_calendar_topics() -> list:
    """Read next week's Instagram posts from the Notion content calendar.

    Calendar runs Monday 1am and plans the week starting next Monday.
    Content agent runs Monday 3am and reads those entries to script them.
    """
    return _fetch_calendar_topics("Instagram")


def fetch_this_weeks_tiktok_topics() -> list:
    """Read next week's TikTok posts from the Notion content calendar."""
    return _fetch_calendar_topics("TikTok")
