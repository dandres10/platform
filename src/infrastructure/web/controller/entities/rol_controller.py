
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.rol.index import (
    RolDelete,
    RolRead,
    RolSave,
    RolUpdate,
)
from src.domain.services.use_cases.entities.rol.index import (
    RolDeleteUseCase,
    RolListUseCase,
    RolReadUseCase,
    RolSaveUseCase,
    RolUpdateUseCase,
)
from src.infrastructure.database.repositories.rol_repository import (
    RolRepository,
)

from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

rol_repository = RolRepository()


class RolController:
    def __init__(self) -> None:
        self.rol_save_use_case = RolSaveUseCase(rol_repository)
        self.rol_update_use_case = RolUpdateUseCase(rol_repository)
        self.rol_list_use_case = RolListUseCase(rol_repository)
        self.rol_delete_use_case = RolDeleteUseCase(rol_repository)
        self.rol_read_use_case = RolReadUseCase(rol_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def save(self, config: Config, params: RolSave) -> Response:
        result_save = self.rol_save_use_case.execute(config=config, params=params)
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
    def update(self, config: Config, params: RolUpdate) -> Response:
        result_update = self.rol_update_use_case.execute(config=config, params=params)
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
        result_list = self.rol_list_use_case.execute(config=config, params=params)
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
    def delete(self, config: Config, params: RolDelete) -> Response:
        result_delete = self.rol_delete_use_case.execute(config=config, params=params)
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
    def read(self, config: Config, params: RolRead) -> Response:
        result_delete = self.rol_read_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
        