
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user_location.index import (
    UserLocationDelete,
    UserLocationRead,
    UserLocationSave,
    UserLocationUpdate,
)
from src.domain.services.use_cases.entities.user_location.index import (
    UserLocationDeleteUseCase,
    UserLocationListUseCase,
    UserLocationReadUseCase,
    UserLocationSaveUseCase,
    UserLocationUpdateUseCase,
)
from src.infrastructure.database.repositories.user_location_repository import (
    UserLocationRepository,
)

from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

user_location_repository = UserLocationRepository()


class UserLocationController:
    def __init__(self) -> None:
        self.user_location_save_use_case = UserLocationSaveUseCase(user_location_repository)
        self.user_location_update_use_case = UserLocationUpdateUseCase(user_location_repository)
        self.user_location_list_use_case = UserLocationListUseCase(user_location_repository)
        self.user_location_delete_use_case = UserLocationDeleteUseCase(user_location_repository)
        self.user_location_read_use_case = UserLocationReadUseCase(user_location_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def save(self, config: Config, params: UserLocationSave) -> Response:
        result_save = self.user_location_save_use_case.execute(config=config, params=params)
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
    def update(self, config: Config, params: UserLocationUpdate) -> Response:
        result_update = self.user_location_update_use_case.execute(config=config, params=params)
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
        result_list = self.user_location_list_use_case.execute(config=config, params=params)
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
    def delete(self, config: Config, params: UserLocationDelete) -> Response:
        result_delete = self.user_location_delete_use_case.execute(config=config, params=params)
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
    def read(self, config: Config, params: UserLocationRead) -> Response:
        result_delete = self.user_location_read_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
        