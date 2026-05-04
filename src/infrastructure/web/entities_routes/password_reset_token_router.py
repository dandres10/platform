# SPEC-006 T7
from fastapi import APIRouter, Depends, status
from pydantic import UUID4

from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.methods.get_config import get_config
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.entities.password_reset_token.index import (
    PasswordResetTokenDelete,
    PasswordResetTokenRead,
    PasswordResetTokenSave,
    PasswordResetTokenUpdate,
)
from src.infrastructure.web.controller.entities.password_reset_token_controller import (
    PasswordResetTokenController,
)


password_reset_token_router = APIRouter(
    prefix="/password-reset-token",
    tags=["PasswordResetToken"],
    responses={404: {"description": "Not found"}},
    include_in_schema=True,
)

password_reset_token_controller = PasswordResetTokenController()


@password_reset_token_router.post(
    "", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def save(
    params: PasswordResetTokenSave, config: Config = Depends(get_config)
) -> Response:
    return await password_reset_token_controller.save(config=config, params=params)


@password_reset_token_router.put(
    "", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def update(
    params: PasswordResetTokenUpdate, config: Config = Depends(get_config)
) -> Response:
    return await password_reset_token_controller.update(config=config, params=params)


@password_reset_token_router.post(
    "/list", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.LIST.value])
@execute_transaction_route(enabled=settings.has_track)
async def list(
    params: Pagination, config: Config = Depends(get_config)
) -> Response:
    return await password_reset_token_controller.list(config=config, params=params)


@password_reset_token_router.delete(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = PasswordResetTokenDelete(id=id)
    return await password_reset_token_controller.delete(
        config=config, params=build_params
    )


@password_reset_token_router.get(
    "/{id}", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def read(id: UUID4, config: Config = Depends(get_config)) -> Response:
    build_params = PasswordResetTokenRead(id=id)
    return await password_reset_token_controller.read(
        config=config, params=build_params
    )
