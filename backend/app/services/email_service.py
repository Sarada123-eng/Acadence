from typing import Any

import resend
from resend.exceptions import NoContentError, ResendError

from app.database.connection import Settings, settings


class EmailConfigurationError(RuntimeError):
    """Raised when email delivery is not configured safely."""


class EmailDeliveryError(RuntimeError):
    """Raised when the email provider cannot deliver a message."""


async def send_email(
    recipient: str,
    subject: str,
    text_body: str,
    html_body: str,
    app_settings: Settings = settings,
) -> str:
    """Send an email through the configured asynchronous provider."""

    api_key = app_settings.RESEND_API_KEY.strip()
    from_address = app_settings.EMAIL_FROM_ADDRESS.strip()
    if not api_key or not from_address:
        raise EmailConfigurationError(
            "Email delivery is not configured."
        )

    sender = from_address
    from_name = app_settings.EMAIL_FROM_NAME.strip()
    if from_name:
        sender = f"{from_name} <{from_address}>"

    params: dict[str, Any] = {
        "from": sender,
        "to": [recipient],
        "subject": subject,
        "text": text_body,
        "html": html_body,
    }

    resend.api_key = api_key
    try:
        response = await resend.Emails.send_async(params)
    except (NoContentError, ResendError, ValueError) as exc:
        raise EmailDeliveryError(
            "Email provider failed to send the message."
        ) from None

    message_id = response.get("id")
    if not message_id:
        raise EmailDeliveryError(
            "Email provider returned no message identifier."
        )

    return message_id
