
from pydantic import UUID4
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.permission.index import (
    PermissionDelete,
    PermissionRead,
    PermissionSave,
    PermissionUpdate,
)
from src.infrastructure.web.controller.entities.permission_controller import (
    PermissionController,
)


permission_router = APIRouter(
    prefix="/permission", tags=["Permission"], responses={404: {"description": "Not found"}}
)

permission_controller = PermissionController()


@permission_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def save(params: PermissionSave, config: Config = Depends(get_config)) -> Response:
    return permission_controller.save(config=config, params=params)


@permission_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: PermissionUpdate, config: Config = Depends(get_config)
) -> Response:
    return permission_controller.update(config=config, params=params)


@permission_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return permission_controller.list(config=config, params=params)


@permission_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = PermissionDelete(id=id)
    return permission_controller.delete(config=config, params=build_params)


@permission_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = PermissionRead(id=id)
    return permission_controller.read(config=config, params=build_params)

    