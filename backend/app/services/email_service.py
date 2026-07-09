import asyncio

import resend
from loguru import logger

from app.core.config import require_resend_credentials, settings
from app.core.exceptions import EmailDeliveryError


class EmailService:
    def __init__(self):
        resend.api_key = require_resend_credentials()

    async def send_tape_email(self, recipient: str, public_token: str) -> None:
        tape_url = f"{settings.public_base_url}/tape/{public_token}"

        logger.info("Sending tape email to {}", recipient)

        params = {
            "from": "onboarding@resend.dev",
            "to": recipient,
            "subject": "Someone made you a tape",
            "html": f"<p>You've got a tape! <a href='{tape_url}'>Listen here</a>.</p>",
        }

        try:
            await asyncio.to_thread(resend.Emails.send, params)
        except Exception as e:
            logger.error("Failed to send tape email to {}: {}", recipient, str(e))
            raise EmailDeliveryError("Could not send tape email")


email_service = EmailService()
