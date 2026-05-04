# SPEC-006 T7
from src.core.classes.async_message import Message
from src.core.config import settings
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.message import MessageCoreEntity
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.password_reset_token.index import (
    PasswordResetTokenDelete,
    PasswordResetTokenRead,
    PasswordResetTokenSave,
    PasswordResetTokenUpdate,
)
from src.domain.services.use_cases.entities.password_reset_token.index import (
    PasswordResetTokenDeleteUseCase,
    PasswordResetTokenListUseCase,
    PasswordResetTokenReadUseCase,
    PasswordResetTokenSaveUseCase,
    PasswordResetTokenUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.password_reset_token_repository import (
    PasswordResetTokenRepository,
)


password_reset_token_repository = PasswordResetTokenRepository()


class PasswordResetTokenController:
    def __init__(self) -> None:
        self.password_reset_token_save_use_case = PasswordResetTokenSaveUseCase(
            password_reset_token_repository
        )
        self.password_reset_token_update_use_case = PasswordResetTokenUpdateUseCase(
            password_reset_token_repository
        )
        self.password_reset_token_list_use_case = PasswordResetTokenListUseCase(
            password_reset_token_repository
        )
        self.password_reset_token_delete_use_case = PasswordResetTokenDeleteUseCase(
            password_reset_token_repository
        )
        self.password_reset_token_read_use_case = PasswordResetTokenReadUseCase(
            password_reset_token_repository
        )
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def save(
        self, config: Config, params: PasswordResetTokenSave
    ) -> Response:
        result = await self.password_reset_token_save_use_case.execute(
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
    async def update(
        self, config: Config, params: PasswordResetTokenUpdate
    ) -> Response:
        result = await self.password_reset_token_update_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_UPDATED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Response:
        result = await self.password_reset_token_list_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
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
    async def delete(
        self, config: Config, params: PasswordResetTokenDelete
    ) -> Response:
        result = await self.password_reset_token_delete_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_DELETION_PERFORMED.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def read(
        self, config: Config, params: PasswordResetTokenRead
    ) -> Response:
        result = await self.password_reset_token_read_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_QUERY_MADE.value
                ),
            ),
        )
