# SPEC-006 T12
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from src.core.classes.password import Password
from src.core.models.access_token import AccessToken
from src.core.models.config import Config
from src.domain.models.business.auth.change_password import ChangePasswordRequest
from src.domain.services.use_cases.business.auth.change_password import (
    ChangePasswordUseCase,
)
from src.tests._mock_utils import make_async_db_mock


def _config(user_id: str) -> Config:
    cfg = Config()
    cfg.token = AccessToken(
        rol_id=str(uuid4()),
        rol_code="USER",
        user_id=user_id,
        location_id=str(uuid4()),
        currency_id=str(uuid4()),
        company_id=str(uuid4()),
        token_expiration_minutes=60,
        permissions=["READ"],
    )
    cfg.async_db = make_async_db_mock()
    cfg.response_type = "object"
    cfg.language = "es"
    return cfg


def _user_with(password_hash: str, user_id):
    return SimpleNamespace(
        id=user_id,
        platform_id=uuid4(),
        password=password_hash,
        email="alice@test.com",
        identification="ID123",
        first_name="Alice",
        last_name="Smith",
        phone=None,
        refresh_token="rt",
        password_changed_at=None,
        state=True,
    )


async def test_change_password_returns_user_not_found_when_uc_fails():
    uc = ChangePasswordUseCase()
    user_id = uuid4()
    cfg = _config(str(user_id))

    with patch.object(
        uc.user_read_uc, "execute", new=AsyncMock(return_value=None)
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Usuario no encontrado"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ChangePasswordRequest(
                old_password="anything",
                new_password="Strong1!Pass",
            ),
        )
    assert isinstance(result, str)


async def test_change_password_rejects_when_old_password_incorrect():
    uc = ChangePasswordUseCase()
    user_id = uuid4()
    cfg = _config(str(user_id))
    user = _user_with(
        password_hash=Password.hash_password("CorrectOld1"),
        user_id=user_id,
    )

    with patch.object(
        uc.user_read_uc, "execute", new=AsyncMock(return_value=user)
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Contraseña actual incorrecta"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ChangePasswordRequest(
                old_password="WrongOld1",
                new_password="Strong1!Pass",
            ),
        )
    assert isinstance(result, str)


async def test_change_password_happy_path_invalidates_tokens_and_returns_none():
    uc = ChangePasswordUseCase()
    user_id = uuid4()
    cfg = _config(str(user_id))
    user = _user_with(
        password_hash=Password.hash_password("CorrectOld1"),
        user_id=user_id,
    )

    delete_active = AsyncMock(return_value=2)

    with patch.object(
        uc.user_read_uc, "execute", new=AsyncMock(return_value=user)
    ), patch.object(
        uc.user_update_uc, "execute", new=AsyncMock(return_value=user)
    ), patch.object(
        uc.password_reset_token_repository,
        "delete_active_for_user",
        new=delete_active,
    ):
        result = await uc.execute(
            config=cfg,
            params=ChangePasswordRequest(
                old_password="CorrectOld1",
                new_password="Strong1!NewPass",
            ),
        )

    assert result is None
    delete_active.assert_awaited_once_with(config=cfg, user_id=user.id)


async def test_change_password_request_rejects_weak_new_password():
    import pytest

    with pytest.raises(Exception) as exc:
        ChangePasswordRequest(
            old_password="anything",
            new_password="weak123",
        )
    assert "uppercase" in str(exc.value) or "8 characters" in str(exc.value)


async def test_change_password_update_failure_returns_str():
    uc = ChangePasswordUseCase()
    user_id = uuid4()
    cfg = _config(str(user_id))
    user = _user_with(
        password_hash=Password.hash_password("CorrectOld1"),
        user_id=user_id,
    )

    with patch.object(
        uc.user_read_uc, "execute", new=AsyncMock(return_value=user)
    ), patch.object(
        uc.user_update_uc, "execute", new=AsyncMock(return_value=None)
    ), patch.object(
        uc.message,
        "get_message",
        new=AsyncMock(return_value="Update failed"),
    ):
        result = await uc.execute(
            config=cfg,
            params=ChangePasswordRequest(
                old_password="CorrectOld1",
                new_password="Strong1!NewPass",
            ),
        )
    assert isinstance(result, str)
