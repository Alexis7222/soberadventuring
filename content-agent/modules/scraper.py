import os
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path

APIPY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
APIPY_BASE_URL = "https://api.apify.com/v2"
APIPY_ACTOR = "nH2AHrwxeTRJoN5hX"

OWN_ACCOUNT = "soberadventuring"

HASHTAGS = [
    "soberlife",
    "sobriety",
    "sobercurious",
    "soberentrepreneur",
    "recoveryispossible",
    "freelancelife",
]

COMPETITOR_ACCOUNTS = [
    "soberglowup_",
    "neuro.liminal",
]

ROOT = Path(__file__).parent.parent
FALLBACK_PATH = ROOT / "fallback_hooks.json"
LOG_PATH = ROOT / "errors.log"

logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)


def _run_actor(actor_input: dict) -> list:
    run_resp = requests.post(
        f"{APIFY_BASE_URL}/acts/{APIFY_ACTOR}/runs",
        params={"token": APIFY_API_TOKEN},
        json=actor_input,
        timeout=30,
    )
    run_resp.raise_for_status()
    run = run_resp.json()["data"]
    run_id = run["id"]
    dataset_id = run["defaultDatasetId"]

    print(f"  Apify run {run_id} started — waiting for results...")
    for attempt in range(60):
        time.sleep(10)
        status_resp = requests.get(
            f"{APIFY_BASE_URL}/actor-runs/{run_id}",
            params={"token": APIFY_API_TOKEN},
            timeout=15,
        )
        status_resp.raise_for_status()
        status = status_resp.json()["data"]["status"]
        print(f"  [{attempt * 10}s] Status: {status}")
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended with status: {status}")

    items_resp = requests.get(
        f"{APIFY_BASE_URL}/datasets/{dataset_id}/items",
        params={"token": APIFY_API_TOKEN, "limit": 200},
        timeout=30,
    )
    items_resp.raise_for_status()
    items = items_resp.json()
    print(f"  Got {len(items) if isinstance(items, list) else 0} items from Apify")
    return items if isinstance(items, list) else []


def _engagement_rate(post: dict) -> float:
    followers = post.get("ownerFollowersCount") or 1
    likes = post.get("likesCount") or 0
    comments = post.get("commentsCount") or 0
    return round((likes + comments) / followers * 100, 2)


def _extract_hook(caption: str) -> str:
    if not caption:
        return ""
    return caption.strip().split("\n")[0][:150]


def _analyze_own_posts(posts: list) -> list:
    scored = []
    for p in posts:
        if p.get("ownerUsername", "").lower() != OWN_ACCOUNT:
            continue
        likes = p.get("likesCount", 0) or 0
        if likes < 0:
            continue
        scored.append({
            "hook": _extract_hook(p.get("caption", "")),
            "likes": likes,
            "comments": p.get("commentsCount", 0) or 0,
            "engagement_rate": _engagement_rate(p),
            "type": p.get("type", "unknown"),
            "url": p.get("url", ""),
        })
    scored.sort(key=lambda x: x["likes"], reverse=True)
    return scored[:10]


def _analyze_trend_posts(posts: list) -> dict:
    scored = []
    for p in posts:
        scored.append({
            "hook": _extract_hook(p.get("caption", "")),
            "likes": p.get("likesCount", 0) or 0,
            "comments": p.get("commentsCount", 0) or 0,
            "engagement_rate": _engagement_rate(p),
            "type": p.get("type", "unknown"),
            "account": p.get("ownerUsername", ""),
        })
    scored.sort(key=lambda x: x["engagement_rate"], reverse=True)
    top = scored[:5]
    return {
        "top_posts": top,
        "top_hooks": [p["hook"] for p in top if p["hook"]],
        "total_analyzed": len(scored),
    }


def _load_fallback() -> dict:
    if FALLBACK_PATH.exists():
        data = json.loads(FALLBACK_PATH.read_text())
        print("  Using fallback hooks from previous successful scrape")
        return data
    print("  Using hardcoded fallback hooks")
    return {
        "top_hooks": [
            "This page supports all pathways to recovery... I'm just glad you're here",
            "Most sober people I've met stay away from bars. I don't.",
            "Feb–April, the air turns apocalyptic. AQI regularly hits 300–500+",
            "Wym addiction? martha was just stressed about office politics",
            "These behaviors are not uncommon, in childhood + adolescence, among people who later struggle with addiction.",
        ],
        "top_posts": [],
        "own_top_posts": [],
        "total_analyzed": 0,
        "scraped_at": "fallback",
    }


def run_research() -> dict:
    if not APIFY_API_TOKEN:
        print("  APIFY_API_TOKEN not set — using fallback")
        return _load_fallback()

    try:
        print("  Scraping @soberadventuring own posts...")
        own_posts_raw = _run_actor({
            "usernames": [OWN_ACCOUNT],
            "resultsType": "posts",
            "resultsLimit": 50,
        })
        own_top_posts = _analyze_own_posts(own_posts_raw)
        print(f"  Own posts scraped: {len(own_top_posts)} top performers identified")

        print("  Scraping hashtag trends...")
        hashtag_posts = _run_actor({
            "hashtags": HASHTAGS,
            "resultsType": "posts",
            "resultsLimit": 15,
        })

        print("  Scraping competitor accounts...")
        competitor_posts = _run_actor({
            "usernames": COMPETITOR_ACCOUNTS,
            "resultsType": "posts",
            "resultsLimit": 20,
        })

        trend_data = _analyze_trend_posts(hashtag_posts + competitor_posts)

        results = {
            **trend_data,
            "own_top_posts": own_top_posts,
            "scraped_at": datetime.utcnow().isoformat(),
        }
        FALLBACK_PATH.write_text(json.dumps(results, indent=2))
        print("  Fallback hooks updated with fresh data")
        return results

    except Exception as exc:
        logging.error(f"Scraper error: {exc}")
        print(f"  Scraper failed: {exc} — using fallback")
        return _load_fallback()
