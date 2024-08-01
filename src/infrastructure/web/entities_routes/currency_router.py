from pydantic import UUID4
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.domain.models.entities.currency.currency_delete import CurrencyDelete
from src.domain.models.entities.currency.currency_read import CurrencyRead
from src.domain.models.entities.currency.currency_save import CurrencySave
from src.domain.models.entities.currency.currency_update import CurrencyUpdate
from src.infrastructure.web.controller.entities.currency_controller import (
    CurrencyController,
)


currency_router = APIRouter(
    prefix="/currency", tags=["Currency"], responses={404: {"description": "Not found"}}
)

currency_controller = CurrencyController()


@currency_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
async def save(params: CurrencySave, config: Config = Depends(get_config)) -> Response:
    return currency_controller.save(config, params)


@currency_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
async def update(
    params: CurrencyUpdate, config: Config = Depends(get_config)
) -> Response:
    return currency_controller.update(config, params)


@currency_router.post(
    "/currencys", status_code=status.HTTP_200_OK, response_model=Response
)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return currency_controller.list(config, params)


@currency_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CurrencyDelete(id=id)
    return currency_controller.delete(config, params=build_params)


@currency_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CurrencyRead(id=id)
    return currency_controller.read(config, params=build_params)
