
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
from src.domain.models.entities.rol_permission.index import (
    RolPermissionDelete,
    RolPermissionRead,
    RolPermissionSave,
    RolPermissionUpdate,
)
from src.infrastructure.web.controller.entities.rol_permission_controller import (
    RolPermissionController,
)


rol_permission_router = APIRouter(
    prefix="/rol-permission", tags=["RolPermission"], responses={404: {"description": "Not found"}}
)

rol_permission_controller = RolPermissionController()


@rol_permission_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: RolPermissionSave, config: Config = Depends(get_config)) -> Response:
    return await rol_permission_controller.save(config=config, params=params)


@rol_permission_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: RolPermissionUpdate, config: Config = Depends(get_config)
) -> Response:
    return await rol_permission_controller.update(config=config, params=params)


@rol_permission_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await rol_permission_controller.list(config=config, params=params)


@rol_permission_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = RolPermissionDelete(id=id)
    return await rol_permission_controller.delete(config=config, params=build_params)


@rol_permission_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = RolPermissionRead(id=id)
    return await rol_permission_controller.read(config=config, params=build_params)

    