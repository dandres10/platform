
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.index import (
    CurrencyDelete,
    CurrencyRead,
    CurrencySave,
    CurrencyUpdate,
)
from src.domain.services.use_cases.entities.currency.index import (
    CurrencyDeleteUseCase,
    CurrencyListUseCase,
    CurrencyReadUseCase,
    CurrencySaveUseCase,
    CurrencyUpdateUseCase,
)
from src.infrastructure.database.repositories.currency_repository import (
    CurrencyRepository,
)

from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

currency_repository = CurrencyRepository()


class CurrencyController:
    def __init__(self) -> None:
        self.currency_save_use_case = CurrencySaveUseCase(currency_repository)
        self.currency_update_use_case = CurrencyUpdateUseCase(currency_repository)
        self.currency_list_use_case = CurrencyListUseCase(currency_repository)
        self.currency_delete_use_case = CurrencyDeleteUseCase(currency_repository)
        self.currency_read_use_case = CurrencyReadUseCase(currency_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def save(self, config: Config, params: CurrencySave) -> Response:
        result_save = self.currency_save_use_case.execute(config=config, params=params)
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
    def update(self, config: Config, params: CurrencyUpdate) -> Response:
        result_update = self.currency_update_use_case.execute(config=config, params=params)
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
        result_list = self.currency_list_use_case.execute(config=config, params=params)
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
    def delete(self, config: Config, params: CurrencyDelete) -> Response:
        result_delete = self.currency_delete_use_case.execute(config=config, params=params)
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
    def read(self, config: Config, params: CurrencyRead) -> Response:
        result_delete = self.currency_read_use_case.execute(config=config, params=params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
        