from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.create_api_token.create_api_token_request import (
    CreateApiTokenRequest,
)
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.models.business.auth.create_user_internal import (
    CreateUserInternalRequest,
    CreateUserInternalResponse,
)
from src.domain.models.business.auth.delete_user_internal import (
    DeleteUserInternalRequest,
    DeleteUserInternalResponse,
)
from src.domain.models.business.auth.update_user_internal import (
    UpdateUserInternalRequest,
    UpdateUserInternalResponse,
)
from src.domain.models.business.auth.delete_user_external import (
    DeleteUserExternalRequest,
    DeleteUserExternalResponse,
)
from uuid import UUID
from src.domain.models.business.auth.create_user_external import (
    CreateUserExternalRequest,
    CreateUserExternalResponse,
)
from src.domain.services.use_cases.business.auth.create_api_token.create_api_token_use_case import (
    CreateApiTokenUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_login_use_case import (
    AuthLoginUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_logout_use_case import (
    AuthLogoutUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_refresh_token_use_case import (
    AuthRefreshTokenUseCase,
)
from src.domain.services.use_cases.business.auth.create_user_internal import (
    CreateUserInternalUseCase,
)
from src.domain.services.use_cases.business.auth.delete_user_internal import (
    DeleteUserInternalUseCase,
)
from src.domain.services.use_cases.business.auth.update_user_internal import (
    UpdateUserInternalUseCase,
)
from src.domain.services.use_cases.business.auth.delete_user_external import (
    DeleteUserExternalUseCase,
)
from src.domain.services.use_cases.business.auth.create_user_external import (
    CreateUserExternalUseCase,
)
from src.core.models.filter import Pagination
from typing import List
from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)
from src.domain.models.business.auth.list_users_external import (
    UserExternalItem
)
from src.domain.services.use_cases.business.auth.users_internal import (
    UsersInternalUseCase,
)
from src.domain.services.use_cases.business.auth.users_external import (
    UsersExternalUseCase,
)
from src.domain.models.business.auth.create_company.index import (
    CreateCompanyRequest,
    CreateCompanyResponse,
)
from src.domain.models.business.auth.delete_company import (
    DeleteCompanyRequest,
    DeleteCompanyResponse,
)
from src.domain.services.use_cases.business.auth.create_company.create_company_use_case import (
    CreateCompanyUseCase,
)
from src.domain.services.use_cases.business.auth.delete_company import (
    DeleteCompanyUseCase,
)


class AuthController:
    def __init__(self) -> None:
        self.message = Message()
        self.auth_login_use_case = AuthLoginUseCase()
        self.auth_refresh_token_use_case = AuthRefreshTokenUseCase()
        self.auth_logout_use_case = AuthLogoutUseCase()
        self.create_api_token_use_case = CreateApiTokenUseCase()
        self.create_user_internal_use_case = CreateUserInternalUseCase()
        self.delete_user_internal_use_case = DeleteUserInternalUseCase()
        self.update_user_internal_use_case = UpdateUserInternalUseCase()
        self.delete_user_external_use_case = DeleteUserExternalUseCase()
        self.create_user_external_use_case = CreateUserExternalUseCase()
        self.users_internal_use_case = UsersInternalUseCase()
        self.users_external_use_case = UsersExternalUseCase()
        self.create_company_use_case = CreateCompanyUseCase()
        self.delete_company_use_case = DeleteCompanyUseCase()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def login(self, config: Config, params: AuthLoginRequest) -> Response:
        result = await self.auth_login_use_case.execute(config=config, params=params)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def refresh_token(self, config: Config) -> Response:
        result = await self.auth_refresh_token_use_case.execute(config=config)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def logout(self, config: Config) -> Response:
        result = await self.auth_logout_use_case.execute(config=config)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def create_api_token(
        self, params: CreateApiTokenRequest, config: Config
    ) -> Response:
        result = await self.create_api_token_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def create_user_internal(
        self, config: Config, params: CreateUserInternalRequest
    ) -> Response[CreateUserInternalResponse]:
        result = await self.create_user_internal_use_case.execute(
            config=config, params=params
        )

        if isinstance(result, str):
            return Response.error(message=result)

        success_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_CREATE_USER_SUCCESS.value
            ),
        )

        return Response.success_temporary_message(
            response=CreateUserInternalResponse(message=success_message),
            message=success_message,
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def create_user_external(
        self, config: Config, params: CreateUserExternalRequest
    ) -> Response[CreateUserExternalResponse]:
        result = await self.create_user_external_use_case.execute(
            config=config, params=params
        )

        if isinstance(result, str):
            return Response.error(None, result)

        success_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_CREATE_USER_EXTERNAL_SUCCESS.value
            ),
        )

        return Response.success_temporary_message(
            response=CreateUserExternalResponse(message=success_message),
            message=success_message,
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def users_internal(
        self, 
        config: Config, 
        params: Pagination
    ) -> Response[List[UserByLocationItem]]:
        result = await self.users_internal_use_case.execute(
            config=config, 
            params=params
        )
        
        # Si el resultado es un string, es un mensaje de error
        if isinstance(result, str):
            return Response.error(response=None, message=result)
        
        if not result:
            return Response.success_temporary_message(
                response=[],
                message=await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                    ),
                ),
            )
        
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_QUERY_MADE.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def users_external(
        self, 
        config: Config, 
        params: Pagination
    ) -> Response[List[UserExternalItem]]:
        result = await self.users_external_use_case.execute(
            config=config, 
            params=params
        )
        
        if not result:
            return Response.success_temporary_message(
                response=[],
                message=await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                    ),
                ),
            )
        
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_QUERY_MADE.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def create_company(
        self, 
        config: Config, 
        params: CreateCompanyRequest
    ) -> Response[CreateCompanyResponse]:
        result = await self.create_company_use_case.execute(
            config=config, 
            params=params
        )
        
        if isinstance(result, str):
            if "exitosamente" not in result.lower() and "successfully" not in result.lower():
                return Response.error(response=None, message=result)
            
            return Response.success_temporary_message(
                response=CreateCompanyResponse(message=result),
                message=result
            )
        
        error_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
            ),
        )
        
        return Response.error(
            response=None, 
            message=error_message
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def delete_user_internal(
        self, config: Config, user_id: UUID
    ) -> Response[DeleteUserInternalResponse]:
        params = DeleteUserInternalRequest(user_id=user_id)
        result = await self.delete_user_internal_use_case.execute(
            config=config, params=params
        )

        if isinstance(result, str):
            return Response.error(response=None, message=result)

        success_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_DELETE_USER_SUCCESS.value
            ),
        )

        return Response.success_temporary_message(
            response=DeleteUserInternalResponse(message=success_message),
            message=success_message,
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def update_user_internal(
        self, config: Config, user_id: UUID, params: UpdateUserInternalRequest
    ) -> Response[UpdateUserInternalResponse]:
        result = await self.update_user_internal_use_case.execute(
            config=config, user_id=user_id, params=params
        )

        if isinstance(result, str):
            return Response.error(response=None, message=result)

        success_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_UPDATE_USER_SUCCESS.value
            ),
        )

        return Response.success_temporary_message(
            response=UpdateUserInternalResponse(message=success_message),
            message=success_message,
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def delete_user_external(
        self, config: Config, user_id: UUID
    ) -> Response[DeleteUserExternalResponse]:
        params = DeleteUserExternalRequest(user_id=user_id)
        result = await self.delete_user_external_use_case.execute(
            config=config, params=params
        )

        if isinstance(result, str):
            return Response.error(response=None, message=result)

        success_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.AUTH_DELETE_USER_EXTERNAL_SUCCESS.value
            ),
        )

        return Response.success_temporary_message(
            response=DeleteUserExternalResponse(message=success_message),
            message=success_message,
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def delete_company(
        self, config: Config, company_id: UUID
    ) -> Response[DeleteCompanyResponse]:
        params = DeleteCompanyRequest(company_id=company_id)
        result = await self.delete_company_use_case.execute(
            config=config, params=params
        )

        if isinstance(result, str):
            return Response.error(response=None, message=result)

        success_message = await self.message.get_message(
            config=config,
            message=MessageCoreEntity(
                key=KEYS_MESSAGES.DELETE_COMPANY_SUCCESS.value
            ),
        )

        return Response.success_temporary_message(
            response=DeleteCompanyResponse(message=success_message),
            message=success_message,
        )
