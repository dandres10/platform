
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user_location_rol.index import (
    UserLocationRolDelete,
    UserLocationRolRead,
    UserLocationRolSave,
    UserLocationRolUpdate,
)
from src.domain.services.use_cases.entities.user_location_rol.index import (
    UserLocationRolDeleteUseCase,
    UserLocationRolListUseCase,
    UserLocationRolReadUseCase,
    UserLocationRolSaveUseCase,
    UserLocationRolUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.user_location_rol_repository import (
    UserLocationRolRepository,
)

from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

user_location_rol_repository = UserLocationRolRepository()


class UserLocationRolController:
    def __init__(self) -> None:
        self.user_location_rol_save_use_case = UserLocationRolSaveUseCase(user_location_rol_repository)
        self.user_location_rol_update_use_case = UserLocationRolUpdateUseCase(user_location_rol_repository)
        self.user_location_rol_list_use_case = UserLocationRolListUseCase(user_location_rol_repository)
        self.user_location_rol_delete_use_case = UserLocationRolDeleteUseCase(user_location_rol_repository)
        self.user_location_rol_read_use_case = UserLocationRolReadUseCase(user_location_rol_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def save(self, config: Config, params: UserLocationRolSave) -> Response:
        result_save = self.user_location_rol_save_use_case.execute(config=config, params=params)
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        return Response.success_temporary_message(
            response=result_save,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_SAVED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def update(self, config: Config, params: UserLocationRolUpdate) -> Response:
        result_update = self.user_location_rol_update_use_case.execute(config=config, params=params)
        if isinstance(result_update, str):
            return Response.error(None, result_update)
        return Response.success_temporary_message(
            response=result_update,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_UPDATED_INFORMATION.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Response:
        result_list = self.user_location_rol_list_use_case.execute(config=config, params=params)
        if isinstance(result_list, str):
            return Response.error(None, result_list)
        return Response.success_temporary_message(
            response=result_list,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def delete(self, config: Config, params: UserLocationRolDelete) -> Response:
        result_delete = self.user_location_rol_delete_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_DELETION_PERFORMED.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def read(self, config: Config, params: UserLocationRolRead) -> Response:
        result_delete = self.user_location_rol_read_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
        