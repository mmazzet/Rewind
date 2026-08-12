import asyncio

import resend
from loguru import logger

from app.core.config import (
    require_resend_credentials,
    require_resend_from_email,
    settings,
)
from app.core.exceptions import EmailDeliveryError


class EmailService:
    def __init__(self):
        resend.api_key = require_resend_credentials()

    async def send_tape_email(
        self, recipient: str, public_token: str, message: str | None = None
    ) -> None:
        tape_url = f"{settings.public_base_url}/tape/{public_token}"

        logger.info("Sending tape email to {}", recipient)

        message_html = f"<p><em>{message}</em></p>" if message else ""

        body = (
            f"{message_html}"
            f"<p>You've got a tape! <a href='{tape_url}'>Listen here</a>.</p>"
        )
        params = {
            "from": require_resend_from_email(),
            "to": recipient,
            "subject": "Someone made you a tape",
            "html": body,
        }

        try:
            await asyncio.to_thread(resend.Emails.send, params)
        except Exception as e:
            logger.error("Failed to send tape email to {}: {}", recipient, str(e))
            raise EmailDeliveryError("Could not send tape email")

    async def send_verification_email(self, recipient: str, token: str) -> None:
        verify_url = f"{settings.public_base_url}/verify-email?token={token}"

        logger.info("Sending verification email to {}", recipient)

        params = {
            "from": require_resend_from_email(),
            "to": recipient,
            "subject": "Verify your Rewind email",
            "html": f"<p>Verify your email: <a href='{verify_url}'>Click here</a>.</p>",
        }

        try:
            await asyncio.to_thread(resend.Emails.send, params)
        except Exception as e:
            logger.error(
                "Failed to send verification email to {}: {}", recipient, str(e)
            )
            raise EmailDeliveryError("Could not send verification email")


email_service = EmailService()
