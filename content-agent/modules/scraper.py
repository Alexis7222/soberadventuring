import os
import json
import time
import logging
import requests
from datetime import datetime
from pathlib import Path

APIFY_API_TOKEN = os.environ.get("APIFY_API_TOKEN", "")
APIFY_BASE_URL = "https://api.apify.com/v2"
APIFY_ACTOR = "apify~instagram-scraper"

HASHTAGS = [
    "soberlife",
    "sobriety",
    "sobercurious",
    "soberentrepreneur",
    "recoveryispossible",
    "freelancelife",
]

COMPETITOR_ACCOUNTS = [
    "sobergirlsociety",
    "thisnakedmind",
    "soberadventuring",
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
    """Start Apify actor, wait for completion, return dataset items."""
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

    for _ in range(60):
        time.sleep(10)
        status = requests.get(
            f"{APIFY_BASE_URL}/actor-runs/{run_id}",
            params={"token": APIFY_API_TOKEN},
            timeout=15,
        ).json()["data"]["status"]
        if status == "SUCCEEDED":
            break
        if status in ("FAILED", "ABORTED", "TIMED-OUT"):
            raise RuntimeError(f"Apify run {run_id} ended: {status}")

    items = requests.get(
        f"{APIFY_BASE_URL}/datasets/{dataset_id}/items",
        params={"token": APIFY_API_TOKEN, "limit": 200},
        timeout=30,
    ).json()
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


def _analyze(posts: list) -> dict:
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
        "scraped_at": datetime.utcnow().isoformat(),
    }


def _load_fallback() -> dict:
    if FALLBACK_PATH.exists():
        return json.loads(FALLBACK_PATH.read_text())
    return {
        "top_hooks": [
            "My museum of failures as a 26 year old addict",
            "5 reasons pot addiction was more insidious than opiates",
            "5 reasons I partake in nightlife alone in sobriety",
            "Gravitating to addiction because of a lack of community",
            "4 childhood behaviors that predicted my addiction",
        ],
        "top_posts": [],
        "total_analyzed": 0,
        "scraped_at": "fallback",
    }


def run_research() -> dict:
    """Scrape hashtags and competitor accounts. Falls back to stored hooks on failure."""
    if not APIFY_API_TOKEN:
        logging.warning("APIFY_API_TOKEN not set — using fallback")
        return _load_fallback()

    try:
        hashtag_urls = [f"https://www.instagram.com/explore/tags/{h}/" for h in HASHTAGS]
        hashtag_posts = _run_actor({
            "directUrls": hashtag_urls,
            "resultsType": "posts",
            "resultsLimit": 15,
        })

        competitor_posts = _run_actor({
            "usernames": COMPETITOR_ACCOUNTS,
            "resultsType": "posts",
            "resultsLimit": 20,
        })

        results = _analyze(hashtag_posts + competitor_posts)
        FALLBACK_PATH.write_text(json.dumps(results, indent=2))
        return results

    except Exception as exc:
        logging.error(f"Scraper error: {exc}")
        return _load_fallback()
