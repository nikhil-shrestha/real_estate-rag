from app.agents.email_agent import email_agent
import logging

logger = logging.getLogger(__name__)


def send_email_via_agent(to: str, subject: str, body: str):
    try:
        prompt = f'Send an email to "{to}" with subject "{subject}" and body "{body}"'
        result = email_agent.run(prompt)
        logger.info(result)
        return result
    except Exception as e:
        logger.exception("Agent failed to send email")
        return f"Failed: {e}"