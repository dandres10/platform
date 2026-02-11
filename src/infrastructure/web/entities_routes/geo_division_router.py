
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.geo_division.index import (
    GeoDivisionDelete,
    GeoDivisionRead,
    GeoDivisionSave,
    GeoDivisionUpdate,
)
from src.infrastructure.web.controller.entities.geo_division_controller import (
    GeoDivisionController,
)


geo_division_router = APIRouter(
    prefix="/geo-division", tags=["GeoDivision"], responses={404: {"description": "Not found"}}
)

geo_division_controller = GeoDivisionController()


@geo_division_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: GeoDivisionSave, config: Config = Depends(get_config)) -> Response:
    return await geo_division_controller.save(config=config, params=params)


@geo_division_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: GeoDivisionUpdate, config: Config = Depends(get_config)
) -> Response:
    return await geo_division_controller.update(config=config, params=params)


@geo_division_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await geo_division_controller.list(config=config, params=params)


@geo_division_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = GeoDivisionDelete(id=id)
    return await geo_division_controller.delete(config=config, params=build_params)


@geo_division_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = GeoDivisionRead(id=id)
    return await geo_division_controller.read(config=config, params=build_params)
