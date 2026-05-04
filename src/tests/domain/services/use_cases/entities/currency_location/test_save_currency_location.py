# SPEC-003 T7 / SPEC-001 PLT-006
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4

from src.core.exceptions import BusinessException
from src.core.enums.keys_errors import KEYS_ERRORS
from src.core.models.config import Config
from src.core.models.access_token import AccessToken
from src.core.enums.permission_type import PERMISSION_TYPE
from src.domain.models.entities.company_currency.index import CompanyCurrency
from src.domain.models.entities.currency_location.index import (
    CurrencyLocation,
    CurrencyLocationSave,
)
from src.domain.services.use_cases.entities.currency_location.currency_location_save_use_case import (
    CurrencyLocationSaveUseCase,
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
    return cfg


async def test_save_happy_path_currency_in_company_currency():
    company_id = uuid4()
    currency_id = uuid4()
    location_id = uuid4()

    list_uc = AsyncMock()
    list_uc.execute = AsyncMock(return_value=[
        CompanyCurrency(id=uuid4(), company_id=company_id, currency_id=currency_id, is_base=True),
    ])

    saved = CurrencyLocation(id=uuid4(), location_id=location_id, currency_id=currency_id, state=True)
    repo = AsyncMock()
    repo.save = AsyncMock(return_value=saved)

    uc = CurrencyLocationSaveUseCase(repo, list_uc)
    result = await uc.execute(
        config=_config(),
        params=CurrencyLocationSave(location_id=location_id, currency_id=currency_id),
    )

    assert result == saved
    repo.save.assert_awaited_once()


async def test_save_currency_not_in_company_currency_raises_plt_006():
    # SPEC-001 PLT-006: currency NO en company_currency rechazada
    company_id = uuid4()
    allowed_currency = uuid4()
    rejected_currency = uuid4()

    list_uc = AsyncMock()
    list_uc.execute = AsyncMock(return_value=[
        CompanyCurrency(id=uuid4(), company_id=company_id, currency_id=allowed_currency, is_base=True),
    ])

    repo = AsyncMock()

    uc = CurrencyLocationSaveUseCase(repo, list_uc)
    with pytest.raises(BusinessException) as exc:
        await uc.execute(
            config=_config(),
            params=CurrencyLocationSave(location_id=uuid4(), currency_id=rejected_currency),
        )
    assert exc.value.code == KEYS_ERRORS.PLT_CURRENCY_NOT_ALLOWED_FOR_COMPANY.value
    repo.save.assert_not_called()


async def test_save_empty_company_currency_raises_plt_006():
    list_uc = AsyncMock()
    list_uc.execute = AsyncMock(return_value="No results")  # str = sin company_currency

    repo = AsyncMock()

    uc = CurrencyLocationSaveUseCase(repo, list_uc)
    with pytest.raises(BusinessException) as exc:
        await uc.execute(
            config=_config(),
            params=CurrencyLocationSave(location_id=uuid4(), currency_id=uuid4()),
        )
    assert exc.value.code == KEYS_ERRORS.PLT_CURRENCY_NOT_ALLOWED_FOR_COMPANY.value
