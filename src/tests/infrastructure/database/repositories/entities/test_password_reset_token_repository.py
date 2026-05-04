# SPEC-006 T6
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.domain.models.entities.password_reset_token.index import (
    PasswordResetTokenSave,
)
from src.domain.services.repositories.entities.i_password_reset_token_repository import (
    IPasswordResetTokenRepository,
)
from src.infrastructure.database.entities.password_reset_token_entity import (
    PasswordResetTokenEntity,
)
from src.infrastructure.database.repositories.entities.password_reset_token_repository import (
    PasswordResetTokenRepository,
)
from src.tests._mock_utils import make_async_db_mock


def _config():
    cfg = SimpleNamespace()
    cfg.async_db = make_async_db_mock()
    cfg.has_track = False
    return cfg


def test_repository_implements_interface():
    repo = PasswordResetTokenRepository()
    assert isinstance(repo, IPasswordResetTokenRepository)


async def test_save_adds_flushes_refreshes_and_returns_mapped_token():
    repo = PasswordResetTokenRepository()
    cfg = _config()

    saved_id = uuid4()
    user_id = uuid4()
    expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)

    async def _refresh(entity):
        entity.id = saved_id
        entity.created_date = datetime.now(timezone.utc).replace(tzinfo=None)
        entity.updated_date = datetime.now(timezone.utc).replace(tzinfo=None)

    cfg.async_db.refresh = AsyncMock(side_effect=_refresh)

    result = await repo.save(
        config=cfg,
        params=PasswordResetTokenSave(
            user_id=user_id,
            token="abc123",
            expires_at=expires,
        ),
    )

    assert result is not None
    assert result.token == "abc123"
    assert result.user_id == user_id
    cfg.async_db.add.assert_called_once()
    cfg.async_db.flush.assert_awaited()


async def test_read_by_token_returns_none_when_not_found():
    repo = PasswordResetTokenRepository()
    cfg = _config()

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None
    cfg.async_db.execute = AsyncMock(return_value=fake_result)

    result = await repo.read_by_token(config=cfg, token="missing")
    assert result is None


async def test_read_by_token_returns_mapped_entity_when_found():
    repo = PasswordResetTokenRepository()
    cfg = _config()

    entity = PasswordResetTokenEntity(
        id=uuid4(),
        user_id=uuid4(),
        token="found",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
        used_at=None,
        state=True,
        created_date=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_date=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = entity
    cfg.async_db.execute = AsyncMock(return_value=fake_result)

    result = await repo.read_by_token(config=cfg, token="found")
    assert result is not None
    assert result.token == "found"


async def test_mark_used_sets_used_at_timestamp():
    repo = PasswordResetTokenRepository()
    cfg = _config()

    target_id = uuid4()
    entity = PasswordResetTokenEntity(
        id=target_id,
        user_id=uuid4(),
        token="t",
        expires_at=datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1),
        used_at=None,
        state=True,
        created_date=datetime.now(timezone.utc).replace(tzinfo=None),
        updated_date=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = entity
    cfg.async_db.execute = AsyncMock(return_value=fake_result)
    cfg.async_db.refresh = AsyncMock()

    result = await repo.mark_used(config=cfg, id=target_id)
    assert result is not None
    assert entity.used_at is not None


async def test_mark_used_returns_none_when_not_found():
    repo = PasswordResetTokenRepository()
    cfg = _config()

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None
    cfg.async_db.execute = AsyncMock(return_value=fake_result)

    result = await repo.mark_used(config=cfg, id=uuid4())
    assert result is None


async def test_delete_active_for_user_returns_rowcount():
    repo = PasswordResetTokenRepository()
    cfg = _config()

    fake_result = MagicMock()
    fake_result.rowcount = 3
    cfg.async_db.execute = AsyncMock(return_value=fake_result)

    affected = await repo.delete_active_for_user(config=cfg, user_id=uuid4())
    assert affected == 3
    cfg.async_db.flush.assert_awaited()
