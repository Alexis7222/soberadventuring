import os
import json
import logging
from datetime import datetime
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")

GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GOOGLE_DRIVE_FOLDER_ID = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
SCOPES = ["https://www.googleapis.com/auth/documents", "https://www.googleapis.com/auth/drive"]


def _get_services():
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    creds = service_account.Credentials.from_service_account_info(
        json.loads(GOOGLE_SERVICE_ACCOUNT_JSON), scopes=SCOPES
    )
    return build("docs", "v1", credentials=creds), build("drive", "v3", credentials=creds)


def _format_carousel(c: dict, index: int) -> str:
    lines = [f"\n{'=' * 50}"]
    lines.append(f"CAROUSEL {index} — {c.get('pillar', '').upper()}")
    if c.get("secondary_pillar"):
        lines.append(f"Also: {c['secondary_pillar']}")
    lines.append(f"Trend link: {c.get('trend_link', '')}")
    lines.append(f"\nSLIDE 1 HOOK: {c.get('slide_1_hook', '')}")
    lines.append(f"Visual direction: {c.get('visual_direction', '')}\n")
    for i, slide in enumerate(c.get("slides", []), 2):
        lines.append(f"SLIDE {i}: {slide}")
    lines.append(f"\nFINAL SLIDE: {c.get('final_slide', '')}")
    lines.append(f"\nCAPTION:\n{c.get('caption', '')}")
    return "\n".join(lines)


def _format_reel(r: dict, index: int) -> str:
    lines = [f"\n{'=' * 50}"]
    lines.append(f"REEL {index} — {r.get('pillar', '').upper()}")
    lines.append(f"Why now: {r.get('why_now', '')}")
    lines.append(f"\nTEXT OVERLAY: {r.get('text_overlay', '')}")
    lines.append(f"VISUAL: {r.get('visual_direction', '')}")
    lines.append(f"AUDIO MOOD: {r.get('audio_mood', '')}")
    return "\n".join(lines)


def _format_monthly(m: dict) -> str:
    lines = [f"\n{'=' * 50}", "MONTHLY LONG-FORM — MUSEUM OF FAILURES"]
    lines.append(f"\nSLIDE 1 HOOK: {m.get('slide_1_hook', '')}\n")
    for slide in m.get("slides", []):
        lines.append(f"SLIDE {slide.get('slide_number', '')}: {slide.get('text', '')}")
        if slide.get("visual"):
            lines.append(f"  Visual: {slide['visual']}")
    lines.append(f"\nFINAL SLIDE:\n{m.get('final_slide_identity', '')}")
    lines.append(f"\nCAPTION:\n{m.get('caption', '')}")
    return "\n".join(lines)


def _build_doc_text(content: dict) -> str:
    week_date = content["week_date"]
    parts = [
        f"CONTENT WEEK OF {week_date.upper()}",
        f"@soberadventuring — Lexi Morgan",
        f"Generated: {datetime.now().strftime('%B %d, %Y %H:%M UTC')}\n",
        "=" * 60,
        "\nTREND REPORT\n",
        content.get("trend_summary", ""),
        "\n\n" + "=" * 60,
        "\nCARROUSELS (6)\n",
    ]
    for i, c in enumerate(content.get("carousels", []), 1):
        parts.append(_format_carousel(c, i))
    parts += ["\n\n" + "=" * 60, "\nSHORT REELS — 6-9 SECONDS (4)\n"]
    for i, r in enumerate(content.get("reels", []), 1):
        parts.append(_format_reel(r, i))
    if content.get("monthly"):
        parts += ["\n\n" + "=" * 60]
        parts.append(_format_monthly(content["monthly"]))
    return "\n".join(parts)


def save_output(content: dict) -> str:
    """Try Google Docs first, fall back to local .md file."""
    week_date = content["week_date"]
    title = f"Content Week of {week_date} — @soberadventuring"
    doc_text = _build_doc_text(content)

    if GOOGLE_SERVICE_ACCOUNT_JSON:
        try:
            docs, drive = _get_services()
            doc = docs.documents().create(body={"title": title}).execute()
            doc_id = doc["documentId"]

            if GOOGLE_DRIVE_FOLDER_ID:
                drive.files().update(
                    fileId=doc_id,
                    addParents=GOOGLE_DRIVE_FOLDER_ID,
                    fields="id, parents",
                ).execute()

            docs.documents().batchUpdate(
                documentId=doc_id,
                body={"requests": [{"insertText": {"location": {"index": 1}, "text": doc_text}}]},
            ).execute()

            url = f"https://docs.google.com/document/d/{doc_id}"
            print(f"  Google Doc: {url}")
            return url

        except Exception as exc:
            logging.error(f"Google Docs failed: {exc}")
            print(f"  Google Docs failed ({exc}) — saving locally")

    fallback = Path(f"content_{week_date.replace(' ', '_').replace(',', '')}.md")
    fallback.write_text(doc_text)
    print(f"  Saved locally: {fallback}")
    return str(fallback)
