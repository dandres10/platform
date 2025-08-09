from fastapi import APIRouter, Depends, status
from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.infrastructure.web.controller.business.auth_controller import AuthController
from src.core.methods.get_config import get_config, get_config_login


auth_router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={404: {"description": "Not found"}}
)

auth_controller = AuthController()


@auth_router.post("/login", status_code=status.HTTP_200_OK, response_model=Response)
@execute_transaction_route(enabled=settings.has_track)
async def login(
    params: AuthLoginRequest, config: Config = Depends(get_config_login)
) -> Response:
    return await auth_controller.login(config=config, params=params)


@auth_router.post(
    "/refresh_token", status_code=status.HTTP_200_OK, response_model=Response
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def refresh_token(config: Config = Depends(get_config)) -> Response:
    return await auth_controller.refresh_token(config=config)


@auth_router.post("/logout", status_code=status.HTTP_200_OK, response_model=Response)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def logout(config: Config = Depends(get_config)) -> Response:
    return await auth_controller.logout(config=config)


@auth_router.post(
    "/create-api-token",
    status_code=status.HTTP_200_OK,
    response_model=Response,
    include_in_schema=True,
)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def create_api_token(
    params: CreateApiTokenRequest, config: Config = Depends(get_config)
) -> Response:
    return await auth_controller.create_api_token(config=config, params=params)
