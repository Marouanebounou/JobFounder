import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date
from pathlib import Path
from jinja2 import Template

from config import SENDER_EMAIL, SENDER_APP_PASSWORD, RECIPIENT_EMAIL


TEMPLATE_PATH = Path(__file__).parent / "templates" / "email_digest.html"


def render_email(jobs: list[dict]) -> str:
    template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
    template = Template(template_text)

    sources = set(job.get("source", "") for job in jobs)
    top_score = max((job.get("match_score", 0) for job in jobs), default=0)

    return template.render(
        date=date.today().strftime("%d/%m/%Y"),
        total_jobs=len(jobs),
        sources_count=len(sources),
        top_score=top_score,
        jobs=jobs,
    )


def send_digest(jobs: list[dict]) -> bool:
    if not jobs:
        print("[Email] No jobs to send. Skipping.")
        return False

    if not SENDER_EMAIL or not SENDER_APP_PASSWORD or not RECIPIENT_EMAIL:
        print("[Email] ERROR: Email credentials not configured in .env")
        return False

    html_content = render_email(jobs)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"JobFounder - {len(jobs)} jobs pour toi ({date.today().strftime('%d/%m')})"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECIPIENT_EMAIL

    plain = f"JobFounder found {len(jobs)} jobs matching your profile today.\n\n"
    for job in jobs[:10]:
        plain += f"- {job['title']} @ {job['company']} ({job['match_score']}% match)\n  {job['url']}\n\n"

    msg.attach(MIMEText(plain, "plain"))
    msg.attach(MIMEText(html_content, "html"))

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"[Email] Digest sent to {RECIPIENT_EMAIL} ({len(jobs)} jobs)")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[Email] ERROR: Authentication failed. Check your App Password.")
        return False
    except Exception as e:
        print(f"[Email] ERROR: {e}")
        return False
