
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency_location.index import (
    CurrencyLocationDelete,
    CurrencyLocationRead,
    CurrencyLocationSave,
    CurrencyLocationUpdate,
)
from src.domain.services.use_cases.entities.currency_location.index import (
    CurrencyLocationDeleteUseCase,
    CurrencyLocationListUseCase,
    CurrencyLocationReadUseCase,
    CurrencyLocationSaveUseCase,
    CurrencyLocationUpdateUseCase,
)
from src.infrastructure.database.repositories.entities.currency_location_repository import (
    CurrencyLocationRepository,
)

from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

currency_location_repository = CurrencyLocationRepository()


class CurrencyLocationController:
    def __init__(self) -> None:
        self.currency_location_save_use_case = CurrencyLocationSaveUseCase(currency_location_repository)
        self.currency_location_update_use_case = CurrencyLocationUpdateUseCase(currency_location_repository)
        self.currency_location_list_use_case = CurrencyLocationListUseCase(currency_location_repository)
        self.currency_location_delete_use_case = CurrencyLocationDeleteUseCase(currency_location_repository)
        self.currency_location_read_use_case = CurrencyLocationReadUseCase(currency_location_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def save(self, config: Config, params: CurrencyLocationSave) -> Response:
        result_save = self.currency_location_save_use_case.execute(config=config, params=params)
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
    def update(self, config: Config, params: CurrencyLocationUpdate) -> Response:
        result_update = self.currency_location_update_use_case.execute(config=config, params=params)
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
        result_list = self.currency_location_list_use_case.execute(config=config, params=params)
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
    def delete(self, config: Config, params: CurrencyLocationDelete) -> Response:
        result_delete = self.currency_location_delete_use_case.execute(config=config, params=params)
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
    def read(self, config: Config, params: CurrencyLocationRead) -> Response:
        result_delete = self.currency_location_read_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
        