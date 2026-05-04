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
    CompanyCurrencyUpdate,
)
from src.domain.services.use_cases.entities.company_currency.update_company_currency_use_case import (
    UpdateCompanyCurrencyUseCase,
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


async def test_update_happy_path():
    target_id = uuid4()
    existing = CompanyCurrency(id=target_id, company_id=uuid4(), currency_id=uuid4(), is_base=False)
    updated = CompanyCurrency(id=target_id, company_id=existing.company_id, currency_id=existing.currency_id, is_base=False, state=True)

    repo = AsyncMock()
    repo.read = AsyncMock(return_value=existing)
    repo.update = AsyncMock(return_value=updated)

    uc = UpdateCompanyCurrencyUseCase(repo)
    result = await uc.execute(config=_config(), params=CompanyCurrencyUpdate(id=target_id, is_base=False))

    assert result == updated
    repo.update.assert_awaited_once()


async def test_update_not_found_raises_plt_004():
    repo = AsyncMock()
    repo.read = AsyncMock(return_value=None)

    uc = UpdateCompanyCurrencyUseCase(repo)
    with pytest.raises(BusinessException) as exc:
        await uc.execute(config=_config(), params=CompanyCurrencyUpdate(id=uuid4(), is_base=True))
    assert exc.value.code == KEYS_ERRORS.PLT_COMPANY_CURRENCY_NOT_FOUND.value


async def test_update_swap_base_demotes_current_base():
    # SPEC-001 R6: cambiar is_base de false→true demota la actual base
    target_id = uuid4()
    company_id = uuid4()
    target = CompanyCurrency(id=target_id, company_id=company_id, currency_id=uuid4(), is_base=False)
    current_base = CompanyCurrency(id=uuid4(), company_id=company_id, currency_id=uuid4(), is_base=True)
    updated_target = CompanyCurrency(id=target_id, company_id=company_id, currency_id=target.currency_id, is_base=True, state=True)

    repo = AsyncMock()
    repo.read = AsyncMock(return_value=target)
    repo.find_base_by_company = AsyncMock(return_value=current_base)
    repo.update = AsyncMock(return_value=updated_target)

    uc = UpdateCompanyCurrencyUseCase(repo)
    result = await uc.execute(config=_config(), params=CompanyCurrencyUpdate(id=target_id, is_base=True))

    assert result == updated_target
    assert repo.update.await_count == 2  # demote current + promote target
    demote_call = repo.update.await_args_list[0]
    assert demote_call.kwargs["params"].id == current_base.id
    assert demote_call.kwargs["params"].is_base is False
