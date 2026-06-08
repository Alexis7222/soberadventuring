#!/usr/bin/env python3
"""
Content Calendar Generator — @soberadventuring
Generates 2 weeks of Instagram, TikTok, and blog content ideas
and populates the Notion content calendar database.

Requires GitHub secrets:
  ANTHROPIC_API_KEY        - Claude API key
  NOTION_API_KEY           - Notion integration token
  NOTION_DATABASE_ID       - ID of the Notion content calendar database
  NOTION_PARENT_PAGE_ID    - Parent page ID (used to create database on first run)
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

SYSTEM_PROMPT = """You are the content strategist for Lexi Morgan (@soberadventuring).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHO LEXI IS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
27, LGBTQ+, 2 years sober, Chiang Mai Thailand, self-employed.
Former addict turned freelance marketing consultant.
Building a 6-figure income from @soberadventuring in public — followers watch in real time.

KNOWN HISTORY (use specific numbers, never vague):
- Arrested by 17
- 16 jobs by age 20
- Dropped out of college three times (enough credits for a master's degree)
- Hospitalised 10 times, survived two suicide attempts
- $20k in debt (paid off in sobriety)
- Cannabis-induced psychosis: 14 days without sleep, believed she was carrying baby Jesus
  while the government was plotting to assassinate her
- 7 cars totaled — doesn't drive anymore ("that's a public service")
- Built Upwork income from $0 to $30k in four months in sobriety, from Thailand

THE BRAND PROMISE: "Build a life so interesting you don't want to escape it."

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
THE BUSINESS — WHAT SHE SELLS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ALIVE Method — sobriety coaching, $395/month, 3-month foundation, free 20-min clarity call
PIVOT Method — career/freelance coaching, $997 flat, 2-month engagement, free 20-min clarity call
Lead magnets: "25 Things Nobody Tells You About Getting Sober" + "What Stage of Recovery Are You In?" quiz
Community: Common Ground Telegram recovery group with weekly meetings

Every piece of content should naturally feed toward one of these. Not with hard sells.
With trust built over time. Followers become clients because they've been watching Lexi build
for months and they trust her completely before they ever speak.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTENT PILLARS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. THE FAILURE ARCHIVE — "By age X, I had already..." structure, specific real numbers, dark humour, identity pivot at end
2. SOBRIETY AS ENTREPRENEURSHIP — same skills: accountability, systems, tolerating discomfort. Feeds PIVOT Method.
3. CONTRARIAN RECOVERY TAKES — pushback on received sober wisdom, personal opinion as fact
4. CONNECTION AS MEDICINE — loneliness as root cause, LGBTQ+ recovery, Rat Park, "I'm just glad you're here"
5. LIFE DESIGN IN SE ASIA — sober + freelance + Thailand, not travel blogging

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
VOICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Sounds like texting a friend who doesn't need things explained to them.
Darkly funny about her past, never self-pitying. Contrarian but means it.
Zero inspirational-poster energy.
Phrases she uses: "to be fair", "thats crazy, by the way..", "IF and only if",
"honestly, that's a public service", "I'm just glad you're here"

Does NOT sound like: a brand, a life coach, a travel blogger, generic wellness content.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WRITING RULES — NON-NEGOTIABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
BANNED STRUCTURES:
- "Not because X. But because Y." — banned in all forms
- "It's not X. It's Y." — banned
- "It's not X, it's Y." — banned
- "isn't X, it's Y" in any clause — banned
- Any two-sentence negative/positive pivot — state the positive directly
- Em dashes — banned everywhere
- Fragment kickers ("Simple." / "Real talk." / "Full stop.") — banned
- Short standalone dramatic sentences stacked for effect — banned

BANNED WORDS: delve into, journey, transformative, game-changer, holistic, leverage,
pivotal, embark, unpack, dive into, at the end of the day, cutting-edge, seamlessly,
robust, comprehensive, tapestry, beacon, resonate, foster, navigate, empower, thrive

Caption opens with a specific fact or statement — never a question, never an emotion.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PLATFORM RULES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Instagram: personal story anchor required. 150-200 word captions. 8-12 hashtags.
  First slide direction: face photo or childhood photo, never a graphic.
TikTok: hook lands in 2 seconds, one relatable moment, works on cold audience.
Blog: SEO-optimised, value-first, 1000-1200 words, written as Alexis Antonelli (coaching voice, not Lexi).
  Blog posts funnel toward ALIVE Method or PIVOT Method with soft CTAs.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WHAT KILLS ENGAGEMENT — NEVER DO THESE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Content any sober creator could post — if it doesn't need Lexi's specific history, reject it
- Pure lifestyle with no recovery angle
- Lists without a personal story anchor
- Overly polished or aspirational tone
- Questions as caption openers"""


SEO_BLOG_TOPICS = [
    "what is sobriety coaching — ALIVE Method",
    "how to build freelance income while sober — PIVOT Method",
    "sobriety coach vs therapist vs sponsor",
    "sober expat life in Chiang Mai Thailand",
    "how to travel sober in Southeast Asia",
    "building remote income in recovery",
    "SMART Recovery vs AA — which is right for you",
    "how to quit drinking without AA",
    "cannabis addiction more insidious than people think",
    "childhood predictors of addiction",
    "Rat Park theory and what it means for your recovery",
    "how to build a sober social life from scratch",
    "the skills sobriety taught me about running a business",
    "first year sober what nobody tells you",
    "how to handle cravings in early sobriety",
    "sober dating as an LGBTQ+ person in recovery",
    "paying off debt in sobriety",
    "how to find community in recovery without AA",
    "building income on Upwork from zero",
    "living in Thailand as a sober freelancer",
]


def create_notion_database(parent_page_id: str) -> str:
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
                        {"name": "Contrarian Take", "color": "orange"},
                        {"name": "Failure Archive", "color": "purple"},
                        {"name": "Building In Public", "color": "pink"}
                    ]
                }
            },
            "Pillar": {"rich_text": {}},
            "Feeds Offer": {"rich_text": {}}
        }
    }
    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    response.raise_for_status()
    db_id = response.json()["id"]
    print(f"Created Notion database: {db_id}")
    return db_id


def generate_weekly_content(week_start: datetime) -> list:
    week_str = week_start.strftime("%B %d, %Y")
    dates = [(week_start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    prompt = f"""Generate a 7-day content calendar for @soberadventuring starting {week_str}.

Available dates: {', '.join(dates)}

Include exactly:
- 3 Instagram posts (Tue, Wed, Thu preferred — highest engagement days)
- 2 TikTok videos (Thu, Sat)
- 1 Blog post (Monday — written as Alexis Antonelli, SEO coaching voice)
- 1 Building In Public update (any day — what Lexi is building this week, raw and real)

MANDATORY REQUIREMENTS:
- At least 1 entry must use the "By age X" Failure Archive structure with real numbers
- At least 1 must be a Contrarian Recovery Take
- At least 1 must anchor in the Sobriety as Entrepreneurship overlap
- The Building In Public post must reference building 6 figures from this Instagram
- Every Instagram post must have a personal story anchor — reject anything generic
- Blog post should soft-funnel toward ALIVE Method or PIVOT Method

Choose blog SEO topic from: {json.dumps(SEO_BLOG_TOPICS[:10])}

Return ONLY a valid JSON array, no markdown fencing:
[
  {{
    "platform": "Instagram",
    "date": "YYYY-MM-DD",
    "title": "Short descriptive title (5-8 words)",
    "content_type": "Educational|Personal Story|Contrarian Take|Failure Archive|Building In Public|Travel|Tips & Practical",
    "pillar": "one of the 5 pillar names",
    "feeds_offer": "ALIVE Method|PIVOT Method|Common Ground|Lead Magnet|None",
    "target_keyword": "main keyword or phrase",
    "draft": "For Instagram: full caption in Lexi voice with specific personal details and hashtags. For TikTok: hook line (lands in 2 seconds) + 3-sentence concept. For Blog: intro paragraph + 5 H2 section titles + soft CTA toward coaching. For Building In Public: raw honest update about what she is actually building this week."
  }}
]

Every entry must feel like it could only have been written by Lexi. Specific numbers, dark humour, real history. Never generic."""

    message = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    if raw.lower().startswith("json"):
        raw = raw[4:]

    return json.loads(raw.strip())


def add_entry_to_notion(database_id: str, entry: dict):
    url = f"{NOTION_BASE_URL}/pages"

    draft_text = entry.get("draft", "")
    if len(draft_text) > 1900:
        draft_text = draft_text[:1900] + "..."

    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Title": {"title": [{"text": {"content": entry["title"]}}]},
            "Platform": {"select": {"name": entry["platform"]}},
            "Date": {"date": {"start": entry["date"]}},
            "Status": {"select": {"name": "Idea"}},
            "Target Keyword": {"rich_text": [{"text": {"content": entry.get("target_keyword", "")}}]},
            "Hook / Caption Draft": {"rich_text": [{"text": {"content": draft_text}}]},
            "Content Type": {"select": {"name": entry.get("content_type", "Personal Story")}},
            "Pillar": {"rich_text": [{"text": {"content": entry.get("pillar", "")}}]},
            "Feeds Offer": {"rich_text": [{"text": {"content": entry.get("feeds_offer", "")}}]},
        }
    }

    response = requests.post(url, headers=NOTION_HEADERS, json=payload)
    response.raise_for_status()
    print(f"  Added: [{entry['platform']}] {entry['title']} ({entry['date']}) → {entry.get('feeds_offer', '')}")


def main():
    global NOTION_DATABASE_ID

    if not NOTION_DATABASE_ID:
        if not NOTION_PARENT_PAGE_ID:
            raise ValueError("Set NOTION_DATABASE_ID or NOTION_PARENT_PAGE_ID")
        print("Creating new Notion database...")
        NOTION_DATABASE_ID = create_notion_database(NOTION_PARENT_PAGE_ID)
        print(f"\nSave this as GitHub secret: NOTION_DATABASE_ID={NOTION_DATABASE_ID}\n")

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
            print(f"Error on week of {week_start.strftime('%B %d')}: {e}")
            raise

    print("\nContent calendar updated.")


if __name__ == "__main__":
    main()
