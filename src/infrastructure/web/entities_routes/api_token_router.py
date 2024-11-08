
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
from src.domain.models.entities.api_token.index import (
    ApiTokenDelete,
    ApiTokenRead,
    ApiTokenSave,
    ApiTokenUpdate,
)
from src.infrastructure.web.controller.entities.api_token_controller import (
    ApiTokenController,
)


api_token_router = APIRouter(
    prefix="/api-token", tags=["ApiToken"], responses={404: {"description": "Not found"}}
)

api_token_controller = ApiTokenController()


@api_token_router.post("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(params: ApiTokenSave, config: Config = Depends(get_config)) -> Response:
    return await api_token_controller.save(config=config, params=params)


@api_token_router.put("", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: ApiTokenUpdate, config: Config = Depends(get_config)
) -> Response:
    return await api_token_controller.update(config=config, params=params)


@api_token_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(params: Pagination, config: Config = Depends(get_config)) -> Response:
    return await api_token_controller.list(config=config, params=params)


@api_token_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = ApiTokenDelete(id=id)
    return await api_token_controller.delete(config=config, params=build_params)


@api_token_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = ApiTokenRead(id=id)
    return await api_token_controller.read(config=config, params=build_params)

    