from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.async_message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.create_api_token.create_api_token_request import CreateApiTokenRequest
from src.domain.models.business.auth.login.auth_login_request import AuthLoginRequest
from src.domain.services.use_cases.business.auth.create_api_token.create_api_token_use_case import CreateApiTokenUseCase
from src.domain.services.use_cases.business.auth.login.auth_login_use_case import (
    AuthLoginUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_logout_use_case import (
    AuthLogoutUseCase,
)
from src.domain.services.use_cases.business.auth.login.auth_refresh_token_use_case import (
    AuthRefreshTokenUseCase,
)


class AuthController:
    def __init__(self) -> None:
        self.message = Message()
        self.auth_login_use_case = AuthLoginUseCase()
        self.auth_refresh_token_use_case = AuthRefreshTokenUseCase()
        self.auth_logout_use_case = AuthLogoutUseCase()
        self.create_api_token_use_case = CreateApiTokenUseCase()

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
    async def create_api_token(self, params: CreateApiTokenRequest, config: Config) -> Response:
        result = await self.create_api_token_use_case.execute(config=config, params=params)
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
