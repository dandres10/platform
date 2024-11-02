
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
from src.domain.models.entities.user_location_rol.index import (
    UserLocationRolDelete,
    UserLocationRolRead,
    UserLocationRolSave,
    UserLocationRolUpdate,
)
from src.infrastructure.web.controller.entities.user_location_rol_controller import (
    UserLocationRolController,
)


user_location_rol_router = APIRouter(
    prefix="/user-location-rol", tags=["UserLocationRol"], responses={404: {"description": "Not found"}}
)

user_location_rol_controller = UserLocationRolController()


@user_location_rol_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: UserLocationRolSave, config: Config = Depends(get_config)) -> Response:
    return await user_location_rol_controller.save(config=config, params=params)


@user_location_rol_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: UserLocationRolUpdate, config: Config = Depends(get_config)
) -> Response:
    return await user_location_rol_controller.update(config=config, params=params)


@user_location_rol_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await user_location_rol_controller.list(config=config, params=params)


@user_location_rol_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = UserLocationRolDelete(id=id)
    return await user_location_rol_controller.delete(config=config, params=build_params)


@user_location_rol_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = UserLocationRolRead(id=id)
    return await user_location_rol_controller.read(config=config, params=build_params)

    