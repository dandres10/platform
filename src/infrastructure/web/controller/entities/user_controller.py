
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user.index import (
    UserDelete,
    UserRead,
    UserSave,
    UserUpdate,
)
from src.domain.services.use_cases.entities.user.index import (
    UserDeleteUseCase,
    UserListUseCase,
    UserReadUseCase,
    UserSaveUseCase,
    UserUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.user_repository import (
    UserRepository,
)



user_repository = UserRepository()


class UserController:
    def __init__(self) -> None:
        self.user_save_use_case = UserSaveUseCase(user_repository)
        self.user_update_use_case = UserUpdateUseCase(user_repository)
        self.user_list_use_case = UserListUseCase(user_repository)
        self.user_delete_use_case = UserDeleteUseCase(user_repository)
        self.user_read_use_case = UserReadUseCase(user_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def save(self, config: Config, params: UserSave) -> Response:
        result_save = await self.user_save_use_case.execute(config=config, params=params)
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        return Response.success_temporary_message(
            response=result_save,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def update(self, config: Config, params: UserUpdate) -> Response:
        result_update = await self.user_update_use_case.execute(config=config, params=params)
        if isinstance(result_update, str):
            return Response.error(None, result_update)
        return Response.success_temporary_message(
            response=result_update,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_UPDATED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Response:
        result_list = await self.user_list_use_case.execute(config=config, params=params)
        if isinstance(result_list, str):
            return Response.error(None, result_list)
        return Response.success_temporary_message(
            response=result_list,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def delete(self, config: Config, params: UserDelete) -> Response:
        result_delete = await self.user_delete_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_DELETION_PERFORMED.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def read(self, config: Config, params: UserRead) -> Response:
        result_delete = await self.user_read_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message= await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
        