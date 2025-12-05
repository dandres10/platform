from fastapi import APIRouter, Depends, status, Path
from uuid import UUID
from src.core.config import settings
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.enums.rol_type import ROL_TYPE
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.wrappers.check_permissions import check_permissions
from src.core.wrappers.check_roles import check_roles
from src.core.wrappers.execute_transaction import execute_transaction_route
from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.create_api_token.create_api_token_response import (
    CreateApiTokenResponse,
)
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.login.auth_login_response import AuthLoginResponse
from src.domain.models.business.auth.logout.auth_logout_response import (
    AuthLogoutResponse,
)
from src.domain.models.business.auth.refresh_token.auth_refresh_token_response import (
    AuthRefreshTokenResponse,
)
from src.domain.models.business.auth.create_user_internal import (
    CreateUserInternalRequest,
    CreateUserInternalResponse,
)
from src.domain.models.business.auth.delete_user_internal import (
    DeleteUserInternalResponse,
)
from src.domain.models.business.auth.delete_user_external import (
    DeleteUserExternalResponse,
)
from src.domain.models.business.auth.create_user_external import (
    CreateUserExternalRequest,
    CreateUserExternalResponse,
)
from src.core.models.filter import Pagination
from typing import List
from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)
from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)
from src.domain.models.business.auth.create_company.index import (
    CreateCompanyRequest,
    CreateCompanyResponse,
)
from src.domain.models.business.auth.delete_company import (
    DeleteCompanyResponse,
)
from src.infrastructure.web.controller.business.auth_controller import AuthController
from src.core.methods.get_config import get_config, get_config_login


auth_router = APIRouter(
    prefix="/auth", tags=["Auth"], responses={404: {"description": "Not found"}}
)

auth_controller = AuthController()


@auth_router.post(
    "/login", status_code=status.HTTP_200_OK, response_model=Response[AuthLoginResponse]
)
@execute_transaction_route(enabled=settings.has_track)
async def login(
    params: AuthLoginRequest, config: Config = Depends(get_config_login)
) -> Response[AuthLoginResponse]:
    return await auth_controller.login(config=config, params=params)


@auth_router.post(
    "/refresh_token",
    status_code=status.HTTP_200_OK,
    response_model=Response[AuthRefreshTokenResponse],
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def refresh_token(
    config: Config = Depends(get_config),
) -> Response[AuthRefreshTokenResponse]:
    return await auth_controller.refresh_token(config=config)


@auth_router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    response_model=Response[AuthLogoutResponse],
)
@check_permissions([PERMISSION_TYPE.UPDATE.value])
@execute_transaction_route(enabled=settings.has_track)
async def logout(config: Config = Depends(get_config)) -> Response[AuthLogoutResponse]:
    return await auth_controller.logout(config=config)


@auth_router.post(
    "/create-api-token",
    status_code=status.HTTP_200_OK,
    response_model=Response[CreateApiTokenResponse],
    include_in_schema=True,
)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@execute_transaction_route(enabled=settings.has_track)
async def create_api_token(
    params: CreateApiTokenRequest, config: Config = Depends(get_config)
) -> Response[CreateApiTokenResponse]:
    return await auth_controller.create_api_token(config=config, params=params)


@auth_router.post(
    "/create-user-internal", status_code=status.HTTP_200_OK, response_model=Response[CreateUserInternalResponse]
)
@check_permissions([PERMISSION_TYPE.SAVE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def create_user_internal(
    params: CreateUserInternalRequest, config: Config = Depends(get_config)
) -> Response[CreateUserInternalResponse]:
    return await auth_controller.create_user_internal(config=config, params=params)


@auth_router.delete(
    "/delete-user-internal/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[DeleteUserInternalResponse]
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete_user_internal(
    user_id: UUID = Path(..., description="ID del usuario interno a eliminar"),
    config: Config = Depends(get_config)
) -> Response[DeleteUserInternalResponse]:
    return await auth_controller.delete_user_internal(config=config, user_id=user_id)


@auth_router.post(
    "/create-user-external",
    status_code=status.HTTP_200_OK,
    response_model=Response[CreateUserExternalResponse]
)
@execute_transaction_route(enabled=settings.has_track)
async def create_user_external(
    params: CreateUserExternalRequest,
    config: Config = Depends(get_config_login)
) -> Response[CreateUserExternalResponse]:
    return await auth_controller.create_user_external(config=config, params=params)


@auth_router.delete(
    "/delete-user-external/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[DeleteUserExternalResponse]
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.USER.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete_user_external(
    user_id: UUID = Path(..., description="ID del usuario externo a eliminar"),
    config: Config = Depends(get_config)
) -> Response[DeleteUserExternalResponse]:
    return await auth_controller.delete_user_external(config=config, user_id=user_id)


@auth_router.post(
    "/users-internal",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[UserByLocationItem]]
)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def users_internal(
    params: Pagination,
    config: Config = Depends(get_config)
) -> Response[List[UserByLocationItem]]:
    return await auth_controller.users_internal(config=config, params=params)


@auth_router.post(
    "/users-external",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[UserExternalItem]]
)
@check_permissions([PERMISSION_TYPE.READ.value])
@execute_transaction_route(enabled=settings.has_track)
async def users_external(
    params: Pagination,
    config: Config = Depends(get_config)
) -> Response[List[UserExternalItem]]:
    return await auth_controller.users_external(config=config, params=params)


@auth_router.post(
    "/create-company",
    status_code=status.HTTP_201_CREATED,
    response_model=Response[CreateCompanyResponse],
    summary="Crear compañía completa",
    description="Endpoint para auto-registro de nuevas compañías con toda su estructura inicial"
)
@execute_transaction_route(enabled=settings.has_track)
async def create_company(
    params: CreateCompanyRequest,
    config: Config = Depends(get_config_login)
) -> Response[CreateCompanyResponse]:
    return await auth_controller.create_company(config=config, params=params)


@auth_router.delete(
    "/delete-company/{company_id}",
    status_code=status.HTTP_200_OK,
    response_model=Response[DeleteCompanyResponse],
    summary="Eliminar compañía",
    description="Elimina una compañía del sistema. Solo un admin de la compañía puede eliminarla."
)
@check_permissions([PERMISSION_TYPE.DELETE.value])
@check_roles([ROL_TYPE.ADMIN.value])
@execute_transaction_route(enabled=settings.has_track)
async def delete_company(
    company_id: UUID = Path(..., description="ID de la compañía a eliminar"),
    config: Config = Depends(get_config)
) -> Response[DeleteCompanyResponse]:
    return await auth_controller.delete_company(config=config, company_id=company_id)
