import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import config
import logging

logger = logging.getLogger(__name__)


def send_email(to_address: str, subject: str, body: str):
    """Send email with enhanced error handling"""
    
    if not config.EMAIL_ENABLED:
        logger.info("Email sending is disabled")
        return
    
    if not config.GMAIL_SENDER or not config.GMAIL_PASSWORD:
        logger.error("Email credentials not configured")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = config.GMAIL_SENDER
        msg['To'] = to_address
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(config.GMAIL_SENDER, config.GMAIL_PASSWORD)
            server.send_message(msg)
            
        logger.info(f"Email sent successfully to {to_address}")
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Email authentication failed. Check credentials.")
        raise
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error occurred: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending email: {e}")
        raise