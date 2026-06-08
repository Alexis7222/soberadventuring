import os
import json
import logging
import requests
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

NOTION_API_KEY = os.environ.get("NOTION_API_KEY", "")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")
NOTION_VERSION = "2022-06-28"

GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]


# ── Notion helpers ──────────────────────────────────────────────────────────

def _notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": NOTION_VERSION,
        "Content-Type": "application/json",
    }


def _text(content: str, bold=False) -> dict:
    return {"type": "text", "text": {"content": content}, "annotations": {"bold": bold}}


def _heading2(text: str) -> dict:
    return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [_text(text)]}}


def _heading3(text: str) -> dict:
    return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [_text(text)]}}


def _paragraph(text: str, bold=False) -> dict:
    return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [_text(text, bold=bold)]}}


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}


def _callout(text: str, emoji: str = "📌") -> dict:
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [_text(text)],
            "icon": {"type": "emoji", "emoji": emoji},
        },
    }


def _build_carousel_blocks(c: dict, index: int) -> list:
    pillar = c.get("pillar", "").upper()
    fmt = c.get("format", "")
    calendar_topic = c.get("calendar_topic", "")
    topic_label = f" | {calendar_topic}" if calendar_topic and calendar_topic != "original" else ""
    blocks = [
        _divider(),
        _heading2(f"CAROUSEL {index} — {pillar}{topic_label}"),
        _callout(f"Format: {fmt} | Pattern: {c.get('performance_pattern', '')}", "🎯"),
        _paragraph(f"Cover hook: {c.get('cover_hook', '')}"),
        _paragraph(f"Cover visual: {c.get('cover_visual', '')}"),
        _heading3("Slides"),
    ]
    for i, slide in enumerate(c.get("slides", []), 1):
        if isinstance(slide, dict):
            header_line = f"[{slide.get('header', f'Slide {i}')}] {slide.get('text', '')}"
            blocks.append(_paragraph(header_line))
            blocks.append(_paragraph(f"  Visual: {slide.get('visual', '')}"))
        else:
            blocks.append(_paragraph(f"Slide {i}: {slide}"))
    blocks += [
        _heading3("Caption"),
        _paragraph(c.get("caption", "")),
        _heading3("Share Hook"),
        _paragraph(c.get("share_hook", "")),
    ]
    return blocks


def _build_reel_blocks(r: dict, index: int) -> list:
    pillar = r.get("pillar", "").upper()
    calendar_topic = r.get("calendar_topic", "")
    topic_label = f" | {calendar_topic}" if calendar_topic and calendar_topic != "original" else ""
    return [
        _divider(),
        _heading2(f"REEL {index} — {pillar}{topic_label}"),
        _callout(f"Text overlay: {r.get('text_overlay', '')}", "🎬"),
        _paragraph(f"Visual: {r.get('visual_direction', '')}"),
        _paragraph(f"Audio mood: {r.get('audio_mood', '')}"),
        _paragraph(f"Why now: {r.get('why_now', '')}"),
    ]


def _build_story_blocks(s: dict, index: int) -> list:
    day = s.get("day", f"Day {index}")
    stype = s.get("type", "").replace("_", " ")
    blocks = [
        _divider(),
        _heading2(f"STORY {index} — {day.upper()} ({stype})"),
        _callout(f"Intention: {s.get('intention', '')}", "💬"),
    ]
    for j, slide in enumerate(s.get("slides", []), 1):
        blocks.append(_heading3(f"Slide {j}"))
        blocks.append(_paragraph(f"Text overlay: {slide.get('text_overlay', '')}"))
        blocks.append(_paragraph(f"Visual: {slide.get('visual', '')}"))
        if slide.get("engagement"):
            blocks.append(_paragraph(f"Engagement: {slide['engagement']}", bold=True))
    return blocks


def _build_monthly_blocks(m: dict) -> list:
    blocks = [
        _divider(),
        _heading2("MONTHLY LONG-FORM — MUSEUM OF FAILURES"),
        _callout(f"Hook: {m.get('slide_1_hook', '')}", "🏛️"),
    ]
    for slide in m.get("slides", []):
        blocks.append(_paragraph(f"Slide {slide.get('slide_number', '')}: {slide.get('text', '')}"))
        if slide.get("visual"):
            blocks.append(_paragraph(f"  Visual: {slide['visual']}"))
    blocks += [
        _heading3("Final Slide"),
        _paragraph(m.get("final_slide_identity", "")),
        _heading3("Caption"),
        _paragraph(m.get("caption", "")),
    ]
    return blocks


def _append_blocks(page_id: str, blocks: list):
    """Append blocks to a Notion page in 100-block chunks (API limit)."""
    offset = 0
    while offset < len(blocks):
        chunk = blocks[offset:offset + 100]
        resp = requests.patch(
            f"https://api.notion.com/v1/blocks/{page_id}/children",
            headers=_notion_headers(),
            json={"children": chunk},
        )
        resp.raise_for_status()
        offset += 100


def _save_to_notion(content: dict) -> str:
    week_date = content["week_date"]
    title = f"Week of {week_date} — @soberadventuring"
    vault_alerts = content.get("vault_alerts", [])

    blocks = [
        _callout(
            f"Generated {datetime.now().strftime('%B %d, %Y %H:%M UTC')} | {content.get('own_posts_summary', '')[:200]}",
            "📊",
        ),
    ]

    if vault_alerts:
        alert_lines = [
            "🔥 GOLD VAULT ALERT — these posts hit 300+ likes and aren't in the vault yet. Grab the slides and add them:"
        ]
        for a in vault_alerts:
            alert_lines.append(f"  • {a['likes']} likes: \"{a['hook']}\"")
        blocks.append(_callout("\n".join(alert_lines), "🔥"))

    carousel_count = len(content.get("carousels", []))
    reel_count = len(content.get("reels", []))
    story_count = len(content.get("stories", []))

    blocks += [
        _heading2("TREND REPORT"),
        _paragraph(content.get("trend_summary", "")),
        _divider(),
        _heading2(f"CAROUSELS ({carousel_count})"),
    ]

    for i, c in enumerate(content.get("carousels", []), 1):
        blocks.extend(_build_carousel_blocks(c, i))

    blocks += [_divider(), _heading2(f"REELS — 6-9 SECONDS ({reel_count})")]
    for i, r in enumerate(content.get("reels", []), 1):
        blocks.extend(_build_reel_blocks(r, i))

    if content.get("stories"):
        blocks += [_divider(), _heading2(f"STORIES — MON–FRI ({story_count})")]
        for i, s in enumerate(content.get("stories", []), 1):
            blocks.extend(_build_story_blocks(s, i))

    if content.get("monthly"):
        blocks.extend(_build_monthly_blocks(content["monthly"]))

    page_resp = requests.post(
        "https://api.notion.com/v1/pages",
        headers=_notion_headers(),
        json={
            "parent": {"page_id": NOTION_PARENT_PAGE_ID},
            "properties": {"title": {"title": [_text(title)]}},
            "children": blocks[:100],
        },
    )
    page_resp.raise_for_status()
    page_id = page_resp.json()["id"]

    if len(blocks) > 100:
        _append_blocks(page_id, blocks[100:])

    url = f"https://notion.so/{page_id.replace('-', '')}"
    print(f"  Notion page: {url}")
    return url


# ── Google Docs fallback ─────────────────────────────────────────────────────

def _get_google_services():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_info(
        json.loads(GOOGLE_SERVICE_ACCOUNT_JSON), scopes=SCOPES
    )
    return build("docs", "v1", credentials=creds), build("drive", "v3", credentials=creds)


def _build_plain_text(content: dict) -> str:
    week_date = content["week_date"]
    lines = [
        f"CONTENT WEEK OF {week_date.upper()}",
        f"@soberadventuring | Generated {datetime.now().strftime('%B %d, %Y %H:%M UTC')}",
        "=" * 60,
    ]

    vault_alerts = content.get("vault_alerts", [])
    if vault_alerts:
        lines.append("\n🔥 GOLD VAULT ALERTS:")
        for a in vault_alerts:
            lines.append(f"  {a['likes']} likes: \"{a['hook']}\"")

    lines += ["\nTREND REPORT\n", content.get("trend_summary", ""), "\n\n" + "=" * 60 + "\nCARROUSELS\n"]

    for i, c in enumerate(content.get("carousels", []), 1):
        lines += [
            f"\n--- CAROUSEL {i} — {c.get('pillar', '').upper()} ({c.get('format', '')}) ---",
            f"Cover hook: {c.get('cover_hook', '')}",
            f"Cover visual: {c.get('cover_visual', '')}",
        ]
        for j, slide in enumerate(c.get("slides", []), 1):
            if isinstance(slide, dict):
                lines.append(f"  [{slide.get('header', '')}] {slide.get('text', '')}")
                lines.append(f"    Visual: {slide.get('visual', '')}")
            else:
                lines.append(f"  Slide {j}: {slide}")
        lines.append(f"Caption: {c.get('caption', '')}")

    lines.append("\n" + "=" * 60 + "\nREELS\n")
    for i, r in enumerate(content.get("reels", []), 1):
        lines += [
            f"\n--- REEL {i} — {r.get('pillar', '').upper()} ---",
            f"Overlay: {r.get('text_overlay', '')}",
            f"Visual: {r.get('visual_direction', '')}",
            f"Audio: {r.get('audio_mood', '')}",
        ]

    if content.get("stories"):
        lines.append("\n" + "=" * 60 + "\nSTORIES\n")
        for i, s in enumerate(content.get("stories", []), 1):
            lines.append(
                f"\n--- STORY {i} — {s.get('day', '').upper()} ({s.get('type', '').replace('_', ' ')}) ---"
            )
            lines.append(f"Intention: {s.get('intention', '')}")
            for j, slide in enumerate(s.get("slides", []), 1):
                lines.append(f"  Slide {j}: {slide.get('text_overlay', '')}")
                lines.append(f"    Visual: {slide.get('visual', '')}")
                if slide.get("engagement"):
                    lines.append(f"    Engagement: {slide['engagement']}")

    return "\n".join(lines)


def _save_to_google_docs(content: dict) -> str:
    week_date = content["week_date"]
    title = f"Content Week of {week_date} — @soberadventuring"
    doc_text = _build_plain_text(content)
    docs, drive = _get_google_services()
    doc = docs.documents().create(body={"title": title}).execute()
    doc_id = doc["documentId"]
    if GOOGLE_DRIVE_FOLDER_ID:
        drive.files().update(fileId=doc_id, addParents=GOOGLE_DRIVE_FOLDER_ID, fields="id, parents").execute()
    docs.documents().batchUpdate(
        documentId=doc_id,
        body={"requests": [{"insertText": {"location": {"index": 1}, "text": doc_text}}]},
    ).execute()
    url = f"https://docs.google.com/document/d/{doc_id}"
    print(f"  Google Doc: {url}")
    return url


# ── Main entry ───────────────────────────────────────────────────────────────

def save_output(content: dict) -> str:
    if NOTION_API_KEY and NOTION_PARENT_PAGE_ID:
        try:
            return _save_to_notion(content)
        except Exception as exc:
            logging.error(f"Notion failed: {exc}")
            print(f"  Notion failed ({exc}) — trying Google Docs")

    if GOOGLE_SERVICE_ACCOUNT_JSON:
        try:
            return _save_to_google_docs(content)
        except Exception as exc:
            logging.error(f"Google Docs failed: {exc}")
            print(f"  Google Docs failed ({exc}) — saving locally")

    week_date = content["week_date"]
    fallback = Path(f"content_{week_date.replace(' ', '_').replace(',', '')}.md")
    fallback.write_text(_build_plain_text(content))
    print(f"  Saved locally: {fallback}")
    return str(fallback)
