# SPEC-003 T6 / SPEC-001
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.exceptions import BusinessException
from src.core.enums.keys_errors import KEYS_ERRORS
from src.core.models.config import Config
from src.core.models.access_token import AccessToken
from src.core.enums.permission_type import PERMISSION_TYPE
from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencySave,
)
from src.domain.services.use_cases.entities.company_currency.save_company_currency_use_case import (
    SaveCompanyCurrencyUseCase,
)
from src.tests._mock_utils import make_async_db_mock


def _config() -> Config:
    cfg = Config()
    cfg.token = AccessToken(
        rol_id=str(uuid4()),
        rol_code="ADMIN",
        user_id=str(uuid4()),
        location_id=str(uuid4()),
        currency_id=str(uuid4()),
        company_id=str(uuid4()),
        token_expiration_minutes=60,
        permissions=[p.value for p in PERMISSION_TYPE],
    )
    cfg.async_db = make_async_db_mock()
    cfg.response_type = "object"
    cfg.language = "es"
    return cfg


def _params(company_id: str, currency_id: str, is_base: bool = True) -> CompanyCurrencySave:
    return CompanyCurrencySave(company_id=company_id, currency_id=currency_id, is_base=is_base)


async def test_save_happy_path_first_currency_is_base():
    repo = AsyncMock()
    repo.list = AsyncMock(return_value=None)
    repo.find_base_by_company = AsyncMock(return_value=None)
    saved = CompanyCurrency(
        id=uuid4(),
        company_id=uuid4(),
        currency_id=uuid4(),
        is_base=True,
        state=True,
    )
    repo.save = AsyncMock(return_value=saved)

    uc = SaveCompanyCurrencyUseCase(repo)
    cfg = _config()
    params = _params(str(saved.company_id), str(saved.currency_id), is_base=True)

    result = await uc.execute(config=cfg, params=params)

    assert result == saved
    repo.save.assert_awaited_once()


async def test_save_currency_duplicate_raises_plt_001():
    company_id = uuid4()
    currency_id = uuid4()
    existing = CompanyCurrency(
        id=uuid4(), company_id=company_id, currency_id=currency_id, is_base=True
    )
    repo = AsyncMock()
    repo.list = AsyncMock(return_value=[existing])
    repo.find_base_by_company = AsyncMock(return_value=existing)

    uc = SaveCompanyCurrencyUseCase(repo)
    cfg = _config()
    params = _params(str(company_id), str(currency_id), is_base=False)

    with pytest.raises(BusinessException) as exc:
        await uc.execute(config=cfg, params=params)
    assert exc.value.code == KEYS_ERRORS.PLT_COMPANY_CURRENCY_DUPLICATE.value
    repo.save.assert_not_called()


async def test_save_base_already_exists_raises_plt_002():
    company_id = uuid4()
    existing_base = CompanyCurrency(
        id=uuid4(), company_id=company_id, currency_id=uuid4(), is_base=True
    )
    repo = AsyncMock()
    repo.list = AsyncMock(return_value=[existing_base])
    repo.find_base_by_company = AsyncMock(return_value=existing_base)

    uc = SaveCompanyCurrencyUseCase(repo)
    cfg = _config()
    params = _params(str(company_id), str(uuid4()), is_base=True)

    with pytest.raises(BusinessException) as exc:
        await uc.execute(config=cfg, params=params)
    assert exc.value.code == KEYS_ERRORS.PLT_COMPANY_CURRENCY_BASE_ALREADY_EXISTS.value
    repo.save.assert_not_called()


async def test_save_first_must_be_base_raises_plt_003():
    repo = AsyncMock()
    repo.list = AsyncMock(return_value=None)
    repo.find_base_by_company = AsyncMock(return_value=None)

    uc = SaveCompanyCurrencyUseCase(repo)
    cfg = _config()
    params = _params(str(uuid4()), str(uuid4()), is_base=False)

    with pytest.raises(BusinessException) as exc:
        await uc.execute(config=cfg, params=params)
    assert exc.value.code == KEYS_ERRORS.PLT_COMPANY_CURRENCY_FIRST_MUST_BE_BASE.value
    repo.save.assert_not_called()
