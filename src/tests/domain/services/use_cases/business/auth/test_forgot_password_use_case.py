# SPEC-006 T13
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.core.models.config import Config
from src.domain.models.business.auth.forgot_password import ForgotPasswordRequest
from src.domain.services.use_cases.business.auth.forgot_password import (
    ForgotPasswordUseCase,
)
from src.tests._mock_utils import make_async_db_mock


def _config() -> Config:
    cfg = Config()
    cfg.async_db = make_async_db_mock()
    cfg.response_type = "object"
    cfg.language = "es"
    return cfg


def _user_with_id(user_id):
    return SimpleNamespace(
        id=user_id,
        email="alice@test.com",
        first_name="Alice",
        last_name="Smith",
    )


async def test_returns_none_silently_when_email_not_found():
    uc = ForgotPasswordUseCase()
    cfg = _config()

    with patch.object(
        uc.user_list_uc, "execute", new=AsyncMock(return_value=None)
    ), patch.object(
        uc.password_reset_token_repository,
        "save",
        new=AsyncMock(),
    ) as save_mock, patch.object(
        uc.send_email_uc, "execute", new=AsyncMock()
    ) as send_mock:
        result = await uc.execute(
            config=cfg,
            params=ForgotPasswordRequest(email="ghost@test.com"),
        )

    assert result is None
    save_mock.assert_not_awaited()
    send_mock.assert_not_awaited()


async def test_returns_none_when_user_list_returns_string_error():
    uc = ForgotPasswordUseCase()
    cfg = _config()

    with patch.object(
        uc.user_list_uc,
        "execute",
        new=AsyncMock(return_value="some error"),
    ), patch.object(
        uc.password_reset_token_repository,
        "save",
        new=AsyncMock(),
    ) as save_mock:
        result = await uc.execute(
            config=cfg,
            params=ForgotPasswordRequest(email="x@test.com"),
        )

    assert result is None
    save_mock.assert_not_awaited()


async def test_happy_path_creates_token_and_sends_email():
    uc = ForgotPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    user = _user_with_id(user_id)

    saved_token = SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        token="abc",
        expires_at=datetime.now(timezone.utc),
        used_at=None,
        state=True,
    )

    save_mock = AsyncMock(return_value=saved_token)
    send_mock = AsyncMock(return_value=True)

    with patch.object(
        uc.user_list_uc, "execute", new=AsyncMock(return_value=[user])
    ), patch.object(
        uc.password_reset_token_repository, "save", new=save_mock
    ), patch.object(
        uc.send_email_uc, "execute", new=send_mock
    ):
        result = await uc.execute(
            config=cfg,
            params=ForgotPasswordRequest(
                email="alice@test.com",
                reset_link_base="https://app.goluti.com/reset-password",
            ),
        )

    assert result is None
    save_mock.assert_awaited_once()
    send_mock.assert_awaited_once()

    sent_params = send_mock.call_args.kwargs["params"]
    assert sent_params.to == "alice@test.com"
    assert "alice@test.com" not in sent_params.template_vars["reset_link"]
    assert "?token=" in sent_params.template_vars["reset_link"]
    assert sent_params.template_vars["name"].startswith("Alice")


async def test_does_not_raise_if_email_send_fails():
    uc = ForgotPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    user = _user_with_id(user_id)

    saved_token = SimpleNamespace(id=uuid4(), user_id=user_id)

    with patch.object(
        uc.user_list_uc, "execute", new=AsyncMock(return_value=[user])
    ), patch.object(
        uc.password_reset_token_repository,
        "save",
        new=AsyncMock(return_value=saved_token),
    ), patch.object(
        uc.send_email_uc,
        "execute",
        new=AsyncMock(side_effect=Exception("smtp boom")),
    ):
        result = await uc.execute(
            config=cfg,
            params=ForgotPasswordRequest(email="alice@test.com"),
        )

    assert result is None


async def test_uses_default_reset_link_base_when_not_provided():
    uc = ForgotPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    user = _user_with_id(user_id)

    send_mock = AsyncMock(return_value=True)

    with patch.object(
        uc.user_list_uc, "execute", new=AsyncMock(return_value=[user])
    ), patch.object(
        uc.password_reset_token_repository,
        "save",
        new=AsyncMock(return_value=SimpleNamespace(id=uuid4())),
    ), patch.object(
        uc.send_email_uc, "execute", new=send_mock
    ):
        await uc.execute(
            config=cfg,
            params=ForgotPasswordRequest(email="alice@test.com"),
        )

    sent_params = send_mock.call_args.kwargs["params"]
    assert sent_params.template_vars["reset_link"].startswith(
        "https://app.goluti.com/reset-password?token="
    )
