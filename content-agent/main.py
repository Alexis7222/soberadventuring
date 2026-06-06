#!/usr/bin/env python3
"""
@soberadventuring Content Agent

Weekly flow:
  1. Scrape trending sobriety content via Apify (hashtags + competitor accounts)
  2. Analyze top hooks and engagement patterns
  3. Generate 6 carousels + 4 short reels (+ monthly long-form on first Monday)
  4. Save to Google Doc (falls back to local .md)
  5. Email summary with doc link

Runs every Monday 8am GMT+7 via GitHub Actions.
Run manually: python manual_run.py
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
    days_until_monday = (7 - today.weekday()) % 7
    week_start = today if days_until_monday == 0 else today + timedelta(days=days_until_monday)
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
    label = f"{carousel_count} carousels, {reel_count} reels" + (" + monthly long-form" if has_monthly else "")
    print(f"  Generated: {label}")

    print("\n[3/4] Saving output...")
    doc_url = save_output(content)

    print("\n[4/4] Sending email summary...")
    send_summary(week_date, doc_url, carousel_count, reel_count, has_monthly)

    print("\nDone.")


if __name__ == "__main__":
    main()
