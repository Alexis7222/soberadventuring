import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

GMAIL_USER = "alexis.m.antonelli@gmail.com"
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
LOG_PATH = Path(__file__).parent.parent / "errors.log"
logging.basicConfig(filename=str(LOG_PATH), level=logging.ERROR, format="%(asctime)s %(levelname)s %(message)s")


def send_summary(week_date: str, doc_url: str, carousel_count: int, reel_count: int, has_monthly: bool):
    if not GMAIL_APP_PASSWORD:
        print(f"  GMAIL_APP_PASSWORD not set — skipping email. Doc: {doc_url}")
        return

    monthly_line = "<li>Monthly Museum of Failures carousel included</li>" if has_monthly else ""
    html = f"""<h2>Content Week of {week_date}</h2>
<p><strong><a href="{doc_url}">Open Google Doc &rarr;</a></strong></p>
<ul>
<li>{carousel_count} carousel concepts (slides, captions, visual directions)</li>
<li>{reel_count} &times; 6-9 second reel scripts</li>
{monthly_line}
</ul>
<p>Based on live trend research from Instagram hashtags and competitor accounts.</p>"""

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"@soberadventuring — Content Week of {week_date}"
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_USER
    msg.attach(MIMEText(html, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        print(f"  Email sent to {GMAIL_USER}")
    except Exception as exc:
        logging.error(f"Gmail SMTP error: {exc}")
        print(f"  Email failed ({exc}) — doc: {doc_url}")
