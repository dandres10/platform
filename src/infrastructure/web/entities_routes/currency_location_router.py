
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.currency_location.index import (
    CurrencyLocationDelete,
    CurrencyLocationRead,
    CurrencyLocationSave,
    CurrencyLocationUpdate,
)
from src.infrastructure.web.controller.entities.currency_location_controller import (
    CurrencyLocationController,
)


currency_location_router = APIRouter(
    prefix="/currency-location", tags=["CurrencyLocation"], responses={404: {"description": "Not found"}}
)

currency_location_controller = CurrencyLocationController()


@currency_location_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def save(params: CurrencyLocationSave, config: Config = Depends(get_config)) -> Response:
    return currency_location_controller.save(config=config, params=params)


@currency_location_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: CurrencyLocationUpdate, config: Config = Depends(get_config)
) -> Response:
    return currency_location_controller.update(config=config, params=params)


@currency_location_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return currency_location_controller.list(config=config, params=params)


@currency_location_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CurrencyLocationDelete(id=id)
    return currency_location_controller.delete(config=config, params=build_params)


@currency_location_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = CurrencyLocationRead(id=id)
    return currency_location_controller.read(config=config, params=build_params)

    