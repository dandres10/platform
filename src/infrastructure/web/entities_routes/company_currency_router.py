
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.enums.rol_type import ROL_TYPE
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.check_roles import check_roles
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.company_currency.index import (
    CompanyCurrencyDelete,
    CompanyCurrencyRead,
    CompanyCurrencySave,
    CompanyCurrencyUpdate,
)
from src.infrastructure.web.controller.entities.company_currency_controller import (
    CompanyCurrencyController,
)


company_currency_router = APIRouter(
    prefix="/company-currency",
    tags=["CompanyCurrency"],
    responses={404: {"description": "Not found"}},
)

company_currency_controller = CompanyCurrencyController()


@company_currency_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: CompanyCurrencySave, config: Config = Depends(get_config)) -> Response:
    return await company_currency_controller.save(config=config, params=params)


@company_currency_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: CompanyCurrencyUpdate, config: Config = Depends(get_config)
) -> Response:
    return await company_currency_controller.update(config=config, params=params)


@company_currency_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@check_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.COLLA.value, ROL_TYPE.USER.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await company_currency_controller.list(config=config, params=params)


@company_currency_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CompanyCurrencyDelete(id=id)
    return await company_currency_controller.delete(config=config, params=build_params)


@company_currency_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@check_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.COLLA.value, ROL_TYPE.USER.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CompanyCurrencyRead(id=id)
    return await company_currency_controller.read(config=config, params=build_params)
