import os
import logging
import requests
from pathlib import Path

SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY", "")
TO_EMAIL = os.environ.get("CONTENT_EMAIL", "alexis.m.antonelli@gmail.com")
FROM_EMAIL = os.environ.get("FROM_EMAIL", "content@soberadventuring.com")
LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")


def send_summary(week_date: str, doc_url: str, carousel_count: int, reel_count: int, has_monthly: bool):
    if not SENDGRID_API_KEY:
        print(f"  SENDGRID_API_KEY not set — skipping email")
        print(f"  Doc: {doc_url}")
        return

    monthly_line = "\n• Monthly Museum of Failures carousel: included" if has_monthly else ""
    body = (
        f"Content for week of {week_date} is ready.\n\n"
        f"{doc_url}\n\n"
        f"This week:\n"
        f"• {carousel_count} carousel concepts (slides, captions, visual directions)\n"
        f"• {reel_count} x 6-9 second reel scripts{monthly_line}\n\n"
        f"All content is based on live trend research from Instagram hashtags "
        f"and competitor account analysis."
    )

    resp = requests.post(
        "https://api.sendgrid.com/v3/mail/send",
        headers={"Authorization": f"Bearer {SENDGRID_API_KEY}", "Content-Type": "application/json"},
        json={
            "personalizations": [{"to": [{"email": TO_EMAIL}]}],
            "from": {"email": FROM_EMAIL},
            "subject": f"@soberadventuring — Content Week of {week_date}",
            "content": [{"type": "text/plain", "value": body}],
        },
        timeout=15,
    )

    if resp.status_code == 202:
        print(f"  Email sent to {TO_EMAIL}")
    else:
        logging.error(f"SendGrid error {resp.status_code}: {resp.text}")
        print(f"  Email failed — doc: {doc_url}")
