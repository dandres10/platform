# SPEC-006 T10
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from src.core.classes.token import Token
from src.core.models.access_token import AccessToken
from src.tests._mock_utils import make_async_db_mock


_TEST_USER_ID = str(uuid4())


def _config_with_token(password_changed_at):
    cfg = SimpleNamespace()
    cfg.token = AccessToken(
        rol_id="r1",
        rol_code="ADMIN",
        user_id=_TEST_USER_ID,
        location_id="l1",
        currency_id="c1",
        company_id="co1",
        token_expiration_minutes=60,
        permissions=["READ"],
        password_changed_at=password_changed_at,
    )
    cfg.async_db = make_async_db_mock()
    cfg.response_type = "object"
    cfg.language = "es"
    return cfg


def _user_read_with(pwd_changed, refresh_token="rt"):
    return SimpleNamespace(
        id=_TEST_USER_ID,
        refresh_token=refresh_token,
        password_changed_at=pwd_changed,
    )


def test_create_access_token_includes_password_changed_at():
    t = Token()
    data = AccessToken(
        rol_id="r1",
        rol_code="ADMIN",
        user_id="u1",
        location_id="l1",
        currency_id="c1",
        company_id="co1",
        token_expiration_minutes=60,
        permissions=["READ"],
        password_changed_at=datetime(2026, 5, 4, 10, 0, 0),
    )
    encoded = t.create_access_token(data)
    decoded = t.verify_token(encoded)
    assert decoded.password_changed_at == datetime(2026, 5, 4, 10, 0, 0)


def test_create_access_token_backward_compat_without_password_changed_at():
    t = Token()
    data = AccessToken(
        rol_id="r1",
        rol_code="ADMIN",
        user_id="u1",
        location_id="l1",
        currency_id="c1",
        company_id="co1",
        token_expiration_minutes=60,
        permissions=["READ"],
    )
    encoded = t.create_access_token(data)
    decoded = t.verify_token(encoded)
    assert decoded.password_changed_at is None


async def test_validate_passes_when_user_password_changed_at_is_null():
    t = Token()
    cfg = _config_with_token(password_changed_at=None)
    user = _user_read_with(pwd_changed=None)

    with patch.object(
        t.user_read_use_case, "execute", new=AsyncMock(return_value=user)
    ):
        await t.validate_has_refresh_token(config=cfg)


async def test_validate_passes_when_jwt_pwd_changed_matches_user():
    t = Token()
    pwd_changed = datetime(2026, 5, 4, 10, 0, 0)
    cfg = _config_with_token(password_changed_at=pwd_changed)
    user = _user_read_with(pwd_changed=pwd_changed)

    with patch.object(
        t.user_read_use_case, "execute", new=AsyncMock(return_value=user)
    ):
        await t.validate_has_refresh_token(config=cfg)


async def test_validate_rejects_when_jwt_pwd_changed_is_older_than_user():
    t = Token()
    cfg = _config_with_token(
        password_changed_at=datetime(2026, 5, 4, 9, 0, 0)
    )
    user = _user_read_with(
        pwd_changed=datetime(2026, 5, 4, 10, 0, 0)
    )

    with patch.object(
        t.user_read_use_case, "execute", new=AsyncMock(return_value=user)
    ):
        with pytest.raises(HTTPException) as exc:
            await t.validate_has_refresh_token(config=cfg)
        assert exc.value.status_code == 401


async def test_validate_rejects_when_jwt_has_no_pwd_changed_but_user_does():
    t = Token()
    cfg = _config_with_token(password_changed_at=None)
    user = _user_read_with(
        pwd_changed=datetime(2026, 5, 4, 10, 0, 0)
    )

    with patch.object(
        t.user_read_use_case, "execute", new=AsyncMock(return_value=user)
    ):
        with pytest.raises(HTTPException) as exc:
            await t.validate_has_refresh_token(config=cfg)
        assert exc.value.status_code == 401


async def test_validate_handles_both_aware_datetimes():
    """SPEC-033: con TIMESTAMPTZ + Pydantic AccessToken, ambos lados son aware."""
    t = Token()
    pwd_changed = datetime(2026, 5, 4, 10, 0, 0, tzinfo=timezone.utc)
    cfg = _config_with_token(password_changed_at=pwd_changed)
    user = _user_read_with(pwd_changed=pwd_changed)

    with patch.object(
        t.user_read_use_case, "execute", new=AsyncMock(return_value=user)
    ):
        await t.validate_has_refresh_token(config=cfg)
