#!/usr/bin/env python3
"""
Content Calendar Generator for Sober Adventuring
Generates weekly Instagram, TikTok, and blog content ideas
and populates a Notion database.

Requires GitHub secrets:
  ANTHROPIC_API_KEY   - Claude API key
  NOTION_API_KEY      - Notion integration token
  NOTION_DATABASE_ID  - ID of the Notion content calendar database
                        (OR set NOTION_PARENT_PAGE_ID to create one on first run)
"""

import os
import json
import requests
from datetime import datetime, timedelta
import anthropic

NOTION_API_KEY = os.environ["NOTION_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json"
}

NOTION_BASE_URL = "https://api.notion.com/v1"

SEO_BLOG_TOPICS = [
    "what is sobriety coaching",
    "how to find a sobriety coach",
    "sobriety coach vs therapist vs sponsor",
    "cost of sobriety coaching",
    "online sobriety coaching",
    "sober travel guide Southeast Asia",
    "alcohol-free destinations",
    "how to travel sober",
    "sober expat life",
    "living abroad without drinking",
    "SMART Recovery vs AA",
    "secular recovery programs",
    "non-12-step recovery",
    "how to quit drinking without AA",
    "alternatives to Alcoholics Anonymous",
    "how to stay sober long term",
    "sober social life",
    "how to handle cravings",
    "building sober habits",
    "sobriety and mental health",
    "how to tell people you don't drink",
    "sober dating tips",
    "alcohol-free social events",
    "coping strategies for sobriety",
    "gray area drinking",
    "mindful drinking",
    "sobriety milestones",
    "first year sober what to expect",
    "sober curious lifestyle",
    "alcohol-free travel tips",
    "Chiang Mai sober expat",
    "remote work and sobriety",
    "Upwork freelancing tips",
    "building income in recovery",
    "life coaching for sober people",
]

SYSTEM_PROMPT = """You are a content strategist for Sober Adventuring, a sobriety coaching and sober travel brand run by Alexis Antonelli.

About Alexis:
- 4+ years working in rehab and mental health spaces
- Uses multiple recovery frameworks: 12 steps, SMART Recovery, Refuge Recovery
- Has a sponsor, attends meetings
- Based in Chiang Mai, Thailand as a sober expat
- Made $30k in 4 months on Upwork as a freelancer
- Target audience: people in early recovery, sober curious, those seeking alternatives to traditional 12-step programs

Brand voice:
- Honest, direct, practical, not preachy
- Value-first: give useful information before asking anything
- No toxic positivity or recovery cliches
- Normalize sober travel and sober expat life
- Show that sobriety can be adventurous and financially independent

Content rules:
- No em dashes
- No banned phrases: delve into, journey, transformative, game-changer, holistic approach, leverage, pivotal, embark on, unpack, dive into, in conclusion, it's important to note, at the end of the day, cutting-edge
- Instagram: visual, personal, community-building. 150-220 word captions. 8-12 hashtags.
- TikTok: hook-first, trending sounds compatible, 60-90 second concept. Open with a pattern interrupt.
- Blog: value-first, SEO-optimized, 1000-1200 words"""


def create_notion_database(parent_page_id: str) -> str:
    """Create the content calendar database in Notion."""
    url = f"{NOTION_BASE_URL}/databases"

    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "Sober Adventuring Content Calendar"}}],
        "properties": {
            "Title": {"title": {}},
            "Platform": {
                "select": {
                    "options": [
                        {"name": "Instagram", "color": "pink"},
                        {"name": "TikTok", "color": "purple"},
                        {"name": "Blog", "color": "blue"}
                    ]
                }
            },
            "Date": {"date": {}},
            "Status": {
                "select": {
                    "options": [
                        {"name": "Idea", "color": "gray"},
                        {"name": "Draft", "color": "yellow"},
                        {"name": "Scheduled", "color": "orange"},
                        {"name": "Published", "color": "green"}
                    ]
                }
            },
            "Target Keyword": {"rich_text": {}},
            "Hook / Caption Draft": {"rich_text": {}},
            "Content Type": {
                "select": {
                    "options": [
                        {"name": "Educational", "color": "blue"},
                        {"name": "Personal Story", "color": "red"},
                        {"name": "Tips & Practical", "color": "green"},
                        {"name": "Travel", "color": "yellow"},
                        {"name": "Motivation", "color": "orange"}
                    ]
                }
            }
        }
    }

    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    response.raise_for_status()
    db_id = response.json()["id"]
    print(f"Created Notion database: {db_id}")
    return db_id


def generate_weekly_content(week_start: datetime) -> list:
    """Use Claude to generate a week of content ideas."""
    week_str = week_start.strftime("%B %d, %Y")
    dates = [(week_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    prompt = f"""Generate a 7-day content calendar for Sober Adventuring starting {week_str}.

Available dates: {', '.join(dates)}

Include exactly:
- 3 Instagram posts (spread across Mon, Wed, Fri)
- 3 TikTok videos (spread across Tue, Thu, Sat or Sun)
- 1 Blog post (Monday)

Choose blog/SEO topics from this list where relevant: {json.dumps(SEO_BLOG_TOPICS[:20], indent=2)}

Return ONLY a JSON array with no markdown fencing, no explanation:
[
  {{
    "platform": "Instagram",
    "date": "YYYY-MM-DD",
    "title": "Short descriptive title (5-8 words)",
    "content_type": "Educational|Personal Story|Tips & Practical|Travel|Motivation",
    "target_keyword": "main keyword or phrase",
    "draft": "Full draft. Instagram: complete caption with hashtags. TikTok: hook line + 3-sentence concept. Blog: intro paragraph + 5 H2 section titles."
  }}
]

Make content specific. Reference Chiang Mai, sober travel, or real recovery tools where relevant. Avoid cliches and banned phrases."""

    message = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    raw = message.content[0].text.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    if raw.lower().startswith("json"):
        raw = raw[4:]

    entries = json.loads(raw.strip())
    return entries


def add_entry_to_notion(database_id: str, entry: dict):
    """Add a single entry to the Notion database."""
    url = f"{NOTION_BASE_URL}/pages"

    draft_text = entry.get("draft", "")
    if len(draft_text) > 1900:
        draft_text = draft_text[:1900] + "..."

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {
                "title": [{"text": {"content": entry["title"]}}]
            },
            "Platform": {
                "select": {"name": entry["platform"]}
            },
            "Date": {
                "date": {"start": entry["date"]}
            },
            "Status": {
                "select": {"name": "Idea"}
            },
            "Target Keyword": {
                "rich_text": [{"text": {"content": entry.get("target_keyword", "")}}]
            },
            "Hook / Caption Draft": {
                "rich_text": [{"text": {"content": draft_text}}]
            },
            "Content Type": {
                "select": {"name": entry.get("content_type", "Educational")}
            }
        }
    }

    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    response.raise_for_status()
    print(f"  Added: [{entry['platform']}] {entry['title']} ({entry['date']})")


def main():
    global NOTION_DATABASE_ID

    if not NOTION_DATABASE_ID:
        if not NOTION_PARENT_PAGE_ID:
            raise ValueError(
                "Set NOTION_DATABASE_ID (existing database) or "
                "NOTION_PARENT_PAGE_ID (to create a new database on first run)"
            )
        print("Creating new Notion database...")
        NOTION_DATABASE_ID = create_notion_database(NOTION_PARENT_PAGE_ID)
        print(f"\nSave this as a GitHub secret for future runs:")
        print(f"  NOTION_DATABASE_ID={NOTION_DATABASE_ID}\n")

    today = datetime.today()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7
    week1_start = today + timedelta(days=days_until_monday)
    week2_start = week1_start + timedelta(weeks=1)

    for week_start in [week1_start, week2_start]:
        print(f"\nGenerating content for week of {week_start.strftime('%B %d')}...")
        try:
            entries = generate_weekly_content(week_start)
            print(f"Generated {len(entries)} entries. Adding to Notion...")
            for entry in entries:
                add_entry_to_notion(NOTION_DATABASE_ID, entry)
        except Exception as e:
            print(f"Error generating week of {week_start.strftime('%B %d')}: {e}")
            raise

    print("\nContent calendar updated successfully.")


if __name__ == "__main__":
    main()
