import os
import unittest
from unittest.mock import AsyncMock, patch

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "30")

from resend.exceptions import ResendError

from app.database.connection import Settings
from app.services.email_service import (
    EmailConfigurationError,
    EmailDeliveryError,
    send_email,
)


class EmailServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.settings = Settings(
            DATABASE_URL="sqlite+pysqlite:///:memory:",
            JWT_SECRET_KEY="test-only-secret",
            RESEND_API_KEY="re_test_key",
            EMAIL_FROM_ADDRESS="no-reply@example.edu",
            EMAIL_FROM_NAME="Acadence",
        )

    @patch("app.services.email_service.resend.Emails.send_async")
    async def test_sends_expected_message_and_returns_provider_id(
        self,
        send_async: AsyncMock,
    ) -> None:
        send_async.return_value = {"id": "email_123"}

        result = await send_email(
            "student@example.edu",
            "Verify your email",
            "Your verification code is 123456.",
            "<p>Your verification code is <strong>123456</strong>.</p>",
            self.settings,
        )

        self.assertEqual(result, "email_123")
        send_async.assert_awaited_once_with(
            {
                "from": "Acadence <no-reply@example.edu>",
                "to": ["student@example.edu"],
                "subject": "Verify your email",
                "text": "Your verification code is 123456.",
                "html": "<p>Your verification code is <strong>123456</strong>.</p>",
            }
        )

    @patch("app.services.email_service.resend.Emails.send_async")
    async def test_missing_api_key_fails_before_provider_call(
        self,
        send_async: AsyncMock,
    ) -> None:
        self.settings.RESEND_API_KEY = ""

        with self.assertRaises(EmailConfigurationError):
            await send_email(
                "student@example.edu",
                "Subject",
                "Text",
                "<p>HTML</p>",
                self.settings,
            )

        send_async.assert_not_awaited()

    @patch("app.services.email_service.resend.Emails.send_async")
    async def test_missing_sender_fails_before_provider_call(
        self,
        send_async: AsyncMock,
    ) -> None:
        self.settings.EMAIL_FROM_ADDRESS = ""

        with self.assertRaises(EmailConfigurationError):
            await send_email(
                "student@example.edu",
                "Subject",
                "Text",
                "<p>HTML</p>",
                self.settings,
            )

        send_async.assert_not_awaited()

    @patch("app.services.email_service.resend.Emails.send_async")
    async def test_provider_errors_are_normalized_without_leaking_details(
        self,
        send_async: AsyncMock,
    ) -> None:
        secret_provider_detail = "provider detail containing re_secret_value"
        send_async.side_effect = ResendError(
            500,
            "application_error",
            secret_provider_detail,
            "",
        )

        with self.assertRaises(EmailDeliveryError) as context:
            await send_email(
                "student@example.edu",
                "Subject",
                "Text",
                "<p>HTML</p>",
                self.settings,
            )

        self.assertNotIn(secret_provider_detail, str(context.exception))
        send_async.assert_awaited_once()

    @patch("app.services.email_service.resend.Emails.send_async")
    async def test_missing_provider_message_id_is_rejected(
        self,
        send_async: AsyncMock,
    ) -> None:
        send_async.return_value = {}

        with self.assertRaises(EmailDeliveryError):
            await send_email(
                "student@example.edu",
                "Subject",
                "Text",
                "<p>HTML</p>",
                self.settings,
            )


if __name__ == "__main__":
    unittest.main()
