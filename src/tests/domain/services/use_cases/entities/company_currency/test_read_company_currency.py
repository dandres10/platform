# SPEC-003 T6 / SPEC-001
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.models.config import Config
from src.core.models.access_token import AccessToken
from src.core.enums.permission_type import PERMISSION_TYPE
from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencyRead,
)
from src.domain.services.use_cases.entities.company_currency.read_company_currency_use_case import (
    ReadCompanyCurrencyUseCase,
)
from src.tests._mock_utils import make_async_db_mock


def _config() -> Config:
    cfg = Config()
    cfg.token = AccessToken(
        rol_id=str(uuid4()), rol_code="ADMIN", user_id=str(uuid4()),
        location_id=str(uuid4()), currency_id=str(uuid4()), company_id=str(uuid4()),
        token_expiration_minutes=60, permissions=[p.value for p in PERMISSION_TYPE],
    )
    cfg.async_db = make_async_db_mock()
    cfg.response_type = "object"
    cfg.language = "es"
    return cfg


async def test_read_happy_path():
    target_id = uuid4()
    target = CompanyCurrency(id=target_id, company_id=uuid4(), currency_id=uuid4(), is_base=True)
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=target)

    uc = ReadCompanyCurrencyUseCase(repo)
    result = await uc.execute(config=_config(), params=CompanyCurrencyRead(id=target_id))

    assert result == target


async def test_read_not_found_returns_message():
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=None)

    uc = ReadCompanyCurrencyUseCase(repo)
    uc.message.get_message = AsyncMock(return_value="Record not found")
    result = await uc.execute(config=_config(), params=CompanyCurrencyRead(id=uuid4()))

    assert result == "Record not found"
    uc.message.get_message.assert_awaited_once()
