# SPEC-006 T14
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.core.models.config import Config
from src.domain.models.business.auth.reset_password import ResetPasswordRequest
from src.domain.services.use_cases.business.auth.reset_password import (
    ResetPasswordUseCase,
)
from src.tests._mock_utils import make_async_db_mock


def _config() -> Config:
    cfg = Config()
    cfg.async_db = make_async_db_mock()
    cfg.response_type = "object"
    cfg.language = "es"
    return cfg


def _user(user_id):
    return SimpleNamespace(
        id=user_id,
        platform_id=uuid4(),
        password="oldhash",
        email="alice@test.com",
        identification="ID123",
        first_name="Alice",
        last_name="Smith",
        phone=None,
        refresh_token="rt",
        password_changed_at=None,
        state=True,
    )


def _token(*, user_id, used_at=None, expires_in_seconds=3600):
    return SimpleNamespace(
        id=uuid4(),
        user_id=user_id,
        token="abc123def456",
        expires_at=datetime.utcnow() + timedelta(seconds=expires_in_seconds),
        used_at=used_at,
        state=True,
    )


async def test_returns_invalid_when_token_does_not_exist():
    uc = ResetPasswordUseCase()
    cfg = _config()

    with patch.object(
        uc.password_reset_token_repository,
        "read_by_token",
        new=AsyncMock(return_value=None),
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Token inválido"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ResetPasswordRequest(
                token="nonexistent_token",
                new_password="Strong1!Pass",
            ),
        )

    assert isinstance(result, str)


async def test_returns_already_used_when_token_used_at_set():
    uc = ResetPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    used_token = _token(user_id=user_id, used_at=datetime.utcnow())

    with patch.object(
        uc.password_reset_token_repository,
        "read_by_token",
        new=AsyncMock(return_value=used_token),
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Token ya usado"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ResetPasswordRequest(
                token="abc123def456",
                new_password="Strong1!Pass",
            ),
        )

    assert isinstance(result, str)


async def test_returns_expired_when_token_past_expiration():
    uc = ResetPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    expired = _token(user_id=user_id, expires_in_seconds=-60)

    with patch.object(
        uc.password_reset_token_repository,
        "read_by_token",
        new=AsyncMock(return_value=expired),
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Token expirado"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ResetPasswordRequest(
                token="abc123def456",
                new_password="Strong1!Pass",
            ),
        )

    assert isinstance(result, str)


async def test_happy_path_marks_used_invalidates_others_returns_none():
    uc = ResetPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    valid_token = _token(user_id=user_id)
    user = _user(user_id)

    mark_used = AsyncMock(return_value=valid_token)
    delete_active = AsyncMock(return_value=2)

    with patch.object(
        uc.password_reset_token_repository,
        "read_by_token",
        new=AsyncMock(return_value=valid_token),
    ), patch.object(
        uc.user_read_uc, "execute", new=AsyncMock(return_value=user)
    ), patch.object(
        uc.user_update_uc, "execute", new=AsyncMock(return_value=user)
    ), patch.object(
        uc.password_reset_token_repository, "mark_used", new=mark_used
    ), patch.object(
        uc.password_reset_token_repository,
        "delete_active_for_user",
        new=delete_active,
    ):
        result = await uc.execute(
            config=cfg,
            params=ResetPasswordRequest(
                token="abc123def456",
                new_password="Strong1!Pass",
            ),
        )

    assert result is None
    mark_used.assert_awaited_once_with(config=cfg, id=valid_token.id)
    delete_active.assert_awaited_once_with(config=cfg, user_id=user.id)


async def test_returns_invalid_when_user_not_found():
    uc = ResetPasswordUseCase()
    cfg = _config()
    user_id = uuid4()
    valid_token = _token(user_id=user_id)

    with patch.object(
        uc.password_reset_token_repository,
        "read_by_token",
        new=AsyncMock(return_value=valid_token),
    ), patch.object(
        uc.user_read_uc, "execute", new=AsyncMock(return_value=None)
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Token inválido"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ResetPasswordRequest(
                token="abc123def456",
                new_password="Strong1!Pass",
            ),
        )

    assert isinstance(result, str)


async def test_request_rejects_weak_new_password():
    import pytest

    with pytest.raises(Exception) as exc:
        ResetPasswordRequest(
            token="abc123def456",
            new_password="weak123",
        )
    assert "uppercase" in str(exc.value) or "8 characters" in str(exc.value)
