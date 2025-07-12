from langchain.tools import tool
from app.config import config
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import logging

logger = logging.getLogger(__name__)

@tool
def send_email(compound_input: str) -> str:
    """
    Send an email using SMTP.

    Input format:
    "to=<recipient>; subject=<subject line>; body=<email body>"
    """
    try:
        parts = dict(part.strip().split("=", 1) for part in compound_input.split("; ") if "=" in part)
        to = parts.get("to")
        subject = parts.get("subject")
        body = parts.get("body")

        if not (to and subject and body):
            raise ValueError("Missing required fields. Must include 'to', 'subject', and 'body'.")

        msg = MIMEText(body, "plain", "utf-8")
        msg["Subject"] = subject
        msg["From"] = formataddr((config.EMAIL_FROM_NAME, config.EMAIL_FROM_ADDRESS))
        msg["To"] = to

        with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT) as server:
            server.starttls()
            server.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to}")
        return f"Email successfully sent to {to} with subject '{subject}'."

    except Exception as e:
        logger.error(f"Failed to send email: {e}")
        return f"Failed to send email: {str(e)}"