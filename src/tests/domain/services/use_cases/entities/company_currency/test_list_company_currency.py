# SPEC-003 T6 / SPEC-001
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.access_token import AccessToken
from src.core.enums.permission_type import PERMISSION_TYPE
from src.domain.models.entities.company_currency.index import CompanyCurrency
from src.domain.services.use_cases.entities.company_currency.list_company_currency_use_case import (
    ListCompanyCurrencyUseCase,
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


async def test_list_happy_path_returns_records():
    rows = [
        CompanyCurrency(id=uuid4(), company_id=uuid4(), currency_id=uuid4(), is_base=True),
        CompanyCurrency(id=uuid4(), company_id=uuid4(), currency_id=uuid4(), is_base=False),
    ]
    repo = AsyncMock()
    repo.list = AsyncMock(return_value=rows)

    uc = ListCompanyCurrencyUseCase(repo)
    result = await uc.execute(config=_config(), params=Pagination(all_data=True))

    assert result == rows
    repo.list.assert_awaited_once()


async def test_list_empty_returns_message():
    repo = AsyncMock()
    repo.list = AsyncMock(return_value=None)

    uc = ListCompanyCurrencyUseCase(repo)
    uc.message.get_message = AsyncMock(return_value="No results found")
    result = await uc.execute(config=_config(), params=Pagination())

    assert result == "No results found"
    uc.message.get_message.assert_awaited_once()
