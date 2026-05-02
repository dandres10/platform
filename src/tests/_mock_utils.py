# SPEC-003 T3
from unittest.mock import AsyncMock, MagicMock


def make_async_db_mock() -> AsyncMock:
    db = AsyncMock()
    tx = MagicMock()
    tx.__aenter__ = AsyncMock(return_value=db)
    tx.__aexit__ = AsyncMock(return_value=None)
    db.begin = MagicMock(return_value=tx)
    return db
