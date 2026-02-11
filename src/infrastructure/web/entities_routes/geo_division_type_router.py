
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
from src.domain.models.entities.geo_division_type.index import (
    GeoDivisionTypeDelete,
    GeoDivisionTypeRead,
    GeoDivisionTypeSave,
    GeoDivisionTypeUpdate,
)
from src.infrastructure.web.controller.entities.geo_division_type_controller import (
    GeoDivisionTypeController,
)


geo_division_type_router = APIRouter(
    prefix="/geo-division-type", tags=["GeoDivisionType"], responses={404: {"description": "Not found"}}
)

geo_division_type_controller = GeoDivisionTypeController()


@geo_division_type_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: GeoDivisionTypeSave, config: Config = Depends(get_config)) -> Response:
    return await geo_division_type_controller.save(config=config, params=params)


@geo_division_type_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: GeoDivisionTypeUpdate, config: Config = Depends(get_config)
) -> Response:
    return await geo_division_type_controller.update(config=config, params=params)


@geo_division_type_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await geo_division_type_controller.list(config=config, params=params)


@geo_division_type_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = GeoDivisionTypeDelete(id=id)
    return await geo_division_type_controller.delete(config=config, params=build_params)


@geo_division_type_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = GeoDivisionTypeRead(id=id)
    return await geo_division_type_controller.read(config=config, params=build_params)
