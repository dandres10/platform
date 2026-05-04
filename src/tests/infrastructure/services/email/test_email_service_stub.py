# SPEC-006 T1
import logging

from src.domain.services.repositories.external.i_email_service import IEmailService
from src.infrastructure.services.email.email_service_stub import EmailServiceStub


async def test_stub_implements_email_service_interface():
    stub = EmailServiceStub()
    assert isinstance(stub, IEmailService)


async def test_stub_send_returns_true():
    stub = EmailServiceStub()
    result = await stub.send(
        to="user@test.com",
        subject="Welcome",
        body="Hello, John",
    )
    assert result is True


async def test_stub_send_logs_email_payload(caplog):
    stub = EmailServiceStub()
    caplog.set_level(
        logging.INFO,
        logger="src.infrastructure.services.email.email_service_stub",
    )

    await stub.send(
        to="user@test.com",
        subject="Reset password",
        body="Click here: https://app/reset?token=abc123",
    )

    assert "[EMAIL STUB]" in caplog.text
    assert "user@test.com" in caplog.text
    assert "Reset password" in caplog.text
    assert "abc123" in caplog.text


async def test_stub_does_not_raise_on_empty_body():
    stub = EmailServiceStub()
    result = await stub.send(to="x@y.com", subject="empty", body="")
    assert result is True
