#!/usr/bin/env python3
"""
@soberadventuring Content Agent

Weekly flow:
  1. Calendar runs Monday 1am UTC — writes this week's topics to Notion
  2. Scrape trending sobriety content via Apify (hashtags + competitor accounts)
  3. Read Notion calendar for this week's Instagram topics
  4. Generate full carousel scripts for those topics (or 6 originals if calendar unavailable)
  5. Generate 4 reels from trend research
  6. Save to Notion page (falls back to Google Doc, then local .md)
  7. Email summary

Runs every Monday 3am UTC via GitHub Actions (2 hours after calendar).
"""

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.scraper import run_research
from modules.scripter import generate_content
from modules.output import save_output
from modules.emailer import send_summary


def main():
    today = datetime.today()
    days_to_next_monday = (7 - today.weekday()) % 7
    if days_to_next_monday == 0:
        days_to_next_monday = 7
    week_start = today + timedelta(days=days_to_next_monday)
    week_date = week_start.strftime("%B %d, %Y")

    print(f"\n@soberadventuring Content Agent — Week of {week_date}")
    print("=" * 60)

    print("\n[1/4] Researching trending content...")
    research = run_research()
    print(f"  Analyzed {research.get('total_analyzed', 0)} posts | Source: {research.get('scraped_at', 'fallback')}")

    print("\n[2/4] Generating content...")
    content = generate_content(research, week_date)
    carousel_count = len(content.get("carousels", []))
    reel_count = len(content.get("reels", []))
    has_monthly = content.get("monthly") is not None
    calendar_count = content.get("calendar_topics_count", 0)
    source = f"{calendar_count} calendar topics" if calendar_count else "freeform generation"
    label = f"{carousel_count} carousels ({source}), {reel_count} reels"
    if has_monthly:
        label += " + monthly long-form"
    print(f"  Generated: {label}")

    print("\n[3/4] Saving output...")
    doc_url = save_output(content)

    print("\n[4/4] Sending email summary...")
    send_summary(week_date, doc_url, carousel_count, reel_count, has_monthly)

    print("\nDone.")


if __name__ == "__main__":
    main()
