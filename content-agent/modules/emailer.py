import os
import logging
import requests
from datetime import datetime, timezone
from pathlib import Path

KIT_API_KEY = os.environ.get("KIT_API_KEY", "")
KIT_BASE_URL = "https://api.kit.com/v4"
LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")


def send_summary(week_date: str, doc_url: str, carousel_count: int, reel_count: int, has_monthly: bool):
    if not KIT_API_KEY:
        print(f"  KIT_API_KEY not set — skipping email. Doc: {doc_url}")
        return

    monthly_line = "<li>Monthly Museum of Failures carousel: included</li>" if has_monthly else ""
    content = f"""<h2>Content Week of {week_date}</h2>
<p><strong><a href="{doc_url}">Open Google Doc &rarr;</a></strong></p>
<ul>
<li>{carousel_count} carousel concepts (slides, captions, visual directions)</li>
<li>{reel_count} &times; 6-9 second reel scripts</li>
{monthly_line}
</ul>
<p>Based on live trend research from Instagram hashtags and competitor accounts.</p>"""

    send_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    resp = requests.post(
        f"{KIT_BASE_URL}/broadcasts",
        headers={
            "Authorization": f"Bearer {KIT_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "subject": f"@soberadventuring — Content Week of {week_date}",
            "content": content,
            "send_at": send_at,
        },
        timeout=15,
    )

    if resp.ok:
        data = resp.json()
        broadcast_id = (data.get("broadcast") or {}).get("id") or data.get("id")
        print(f"  Kit broadcast sent (id: {broadcast_id})")
    else:
        logging.error(f"Kit API error {resp.status_code}: {resp.text}")
        print(f"  Kit email failed ({resp.status_code}) — doc: {doc_url}")
