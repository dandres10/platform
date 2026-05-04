# SPEC-006 T2
from unittest.mock import AsyncMock, patch

from src.core.models.config import Config
from src.domain.models.business.notifications.send_email_request import (
    SendEmailRequest,
)
from src.domain.services.use_cases.business.notifications.send_email_use_case import (
    SendEmailUseCase,
    _render_template,
)


def _config() -> Config:
    cfg = Config()
    cfg.language = "es"
    cfg.async_db = AsyncMock()
    cfg.response_type = "object"
    return cfg


def test_render_template_substitutes_vars():
    template = "Hola {{name}}, tu token es {{token}}."
    rendered = _render_template(template, {"name": "Alice", "token": "abc123"})
    assert rendered == "Hola Alice, tu token es abc123."


def test_render_template_keeps_unknown_placeholders():
    template = "Hola {{name}}, {{missing}} sigue ahí."
    rendered = _render_template(template, {"name": "Alice"})
    assert rendered == "Hola Alice, {{missing}} sigue ahí."


def test_render_template_with_empty_vars_returns_original():
    template = "Sin variables."
    assert _render_template(template, {}) == "Sin variables."
    assert _render_template(template, None) == "Sin variables."


async def test_execute_resolves_templates_and_calls_send():
    fake_email_service = AsyncMock()
    fake_email_service.send = AsyncMock(return_value=True)

    uc = SendEmailUseCase(email_service=fake_email_service)

    with patch.object(uc.message, "get_message", new=AsyncMock()) as mock_get:
        mock_get.side_effect = [
            "Bienvenido {{name}}",
            "Hola {{name}}, tu cuenta está activa.",
        ]

        result = await uc.execute(
            config=_config(),
            params=SendEmailRequest(
                to="alice@test.com",
                subject_key="email_welcome_subject",
                body_key="email_welcome_body",
                template_vars={"name": "Alice"},
            ),
        )

    assert result is True
    fake_email_service.send.assert_awaited_once_with(
        to="alice@test.com",
        subject="Bienvenido Alice",
        body="Hola Alice, tu cuenta está activa.",
    )


async def test_execute_returns_error_when_subject_template_missing():
    fake_email_service = AsyncMock()
    fake_email_service.send = AsyncMock(return_value=True)

    uc = SendEmailUseCase(email_service=fake_email_service)

    with patch.object(uc.message, "get_message", new=AsyncMock()) as mock_get:
        mock_get.side_effect = ["Message not configurated", "body"]

        result = await uc.execute(
            config=_config(),
            params=SendEmailRequest(
                to="x@y.com",
                subject_key="missing_key",
                body_key="email_welcome_body",
            ),
        )

    assert isinstance(result, str)
    assert "missing_key" in result
    fake_email_service.send.assert_not_awaited()


async def test_execute_overrides_language_temporarily():
    fake_email_service = AsyncMock()
    fake_email_service.send = AsyncMock(return_value=True)

    uc = SendEmailUseCase(email_service=fake_email_service)
    cfg = _config()
    cfg.language = "es"

    seen_languages: list[str] = []

    async def _capture_get_message(config, message):
        seen_languages.append(config.language)
        return "tpl"

    with patch.object(uc.message, "get_message", new=_capture_get_message):
        await uc.execute(
            config=cfg,
            params=SendEmailRequest(
                to="x@y.com",
                subject_key="k",
                body_key="b",
                language="en",
            ),
        )

    assert seen_languages == ["en", "en"]
    assert cfg.language == "es"


async def test_execute_uses_default_stub_when_no_email_service_provided():
    uc = SendEmailUseCase()

    from src.infrastructure.services.email.email_service_stub import EmailServiceStub

    assert isinstance(uc.email_service, EmailServiceStub)
