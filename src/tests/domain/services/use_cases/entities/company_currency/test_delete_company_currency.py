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
    CompanyCurrencyDelete,
)
from src.domain.services.use_cases.entities.company_currency.delete_company_currency_use_case import (
    DeleteCompanyCurrencyUseCase,
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


async def test_delete_happy_path_non_base():
    target_id = uuid4()
    target = CompanyCurrency(id=target_id, company_id=uuid4(), currency_id=uuid4(), is_base=False)

    repo = AsyncMock()
    repo.read = AsyncMock(return_value=target)
    repo.delete = AsyncMock(return_value=target)

    uc = DeleteCompanyCurrencyUseCase(repo)
    result = await uc.execute(config=_config(), params=CompanyCurrencyDelete(id=target_id))

    assert result == target
    repo.delete.assert_awaited_once()


async def test_delete_not_found_raises_plt_004():
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=None)

    uc = DeleteCompanyCurrencyUseCase(repo)
    with pytest.raises(BusinessException) as exc:
        await uc.execute(config=_config(), params=CompanyCurrencyDelete(id=uuid4()))
    assert exc.value.code == KEYS_ERRORS.PLT_COMPANY_CURRENCY_NOT_FOUND.value


async def test_delete_base_with_alternative_succeeds():
    # SPEC-001: borrar base permitido si hay otra currency en la company
    target_id = uuid4()
    company_id = uuid4()
    target = CompanyCurrency(id=target_id, company_id=company_id, currency_id=uuid4(), is_base=True)
    alternative = CompanyCurrency(id=uuid4(), company_id=company_id, currency_id=uuid4(), is_base=False)

    repo = AsyncMock()
    repo.read = AsyncMock(return_value=target)
    repo.find_base_by_company = AsyncMock(return_value=target)
    repo.list = AsyncMock(return_value=[target, alternative])
    repo.delete = AsyncMock(return_value=target)

    uc = DeleteCompanyCurrencyUseCase(repo)
    result = await uc.execute(config=_config(), params=CompanyCurrencyDelete(id=target_id))

    assert result == target
    repo.delete.assert_awaited_once()


async def test_delete_only_base_raises_plt_005():
    # SPEC-001: no se puede borrar la única company_currency cuando es base
    target_id = uuid4()
    company_id = uuid4()
    target = CompanyCurrency(id=target_id, company_id=company_id, currency_id=uuid4(), is_base=True)

    repo = AsyncMock()
    repo.read = AsyncMock(return_value=target)
    repo.find_base_by_company = AsyncMock(return_value=target)
    repo.list = AsyncMock(return_value=[target])

    uc = DeleteCompanyCurrencyUseCase(repo)
    with pytest.raises(BusinessException) as exc:
        await uc.execute(config=_config(), params=CompanyCurrencyDelete(id=target_id))
    assert exc.value.code == KEYS_ERRORS.PLT_COMPANY_CURRENCY_BASE_REQUIRED.value
    repo.delete.assert_not_called()
