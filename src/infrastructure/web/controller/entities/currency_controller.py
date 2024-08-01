from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.currency.currency_delete import CurrencyDelete
from src.domain.models.entities.currency.currency_read import CurrencyRead
from src.domain.models.entities.currency.currency_save import CurrencySave
from src.domain.models.entities.currency.currency_update import CurrencyUpdate
from src.domain.services.use_cases.entities.currency.currency_delete_use_case import (
    CurrencyDeleteUseCase,
)
from src.domain.services.use_cases.entities.currency.currency_list_use_case import (
    CurrencyListUseCase,
)
from src.domain.services.use_cases.entities.currency.currency_read_use_case import (
    CurrencyReadUseCase,
)
from src.domain.services.use_cases.entities.currency.currency_save_use_case import (
    CurrencySaveUseCase,
)
from src.domain.services.use_cases.entities.currency.currency_update_use_case import (
    CurrencyUpdateUseCase,
)
from src.infrastructure.database.repositories.currency_repository import (
    CurrencyRepository,
)

currency_repository = CurrencyRepository()


class CurrencyController:
    def __init__(self) -> None:
        self.currency_save_use_case = CurrencySaveUseCase(currency_repository)
        self.currency_update_use_case = CurrencyUpdateUseCase(currency_repository)
        self.currency_list_use_case = CurrencyListUseCase(currency_repository)
        self.currency_delete_use_case = CurrencyDeleteUseCase(currency_repository)
        self.currency_read_use_case = CurrencyReadUseCase(currency_repository)

    def save(self, config: Config, params: CurrencySave) -> Response:
        result_save = self.currency_save_use_case.execute(config, params)
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        return Response.success_temporary_message(
            response=result_save, message="Información guarda"
        )

    def update(self, config: Config, params: CurrencyUpdate) -> Response:
        result_update = self.currency_update_use_case.execute(config, params)
        if isinstance(result_update, str):
            return Response.error(None, result_update)
        return Response.success_temporary_message(
            response=result_update, message="Información actualizada"
        )

    def list(self, config: Config, params: Pagination) -> Response:
        result_list = self.currency_list_use_case.execute(config, params)
        if isinstance(result_list, str):
            return Response.error(None, result_list)
        return Response.success_temporary_message(
            response=result_list, message="Consulta realizada"
        )

    def delete(self, config: Config, params: CurrencyDelete) -> Response:
        result_delete = self.currency_delete_use_case.execute(config, params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete, message="Eliminación realizada"
        )

    def read(self, config: Config, params: CurrencyRead) -> Response:
        result_delete = self.currency_read_use_case.execute(config, params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete, message="Consulta realizada"
        )


if settings.has_track:
    CurrencyController.save = execute_transaction(LAYER.I_W_C_E.value)(
        CurrencyController.save
    )
    CurrencyController.update = execute_transaction(LAYER.I_W_C_E.value)(
        CurrencyController.update
    )
    CurrencyController.list = execute_transaction(LAYER.I_W_C_E.value)(
        CurrencyController.list
    )
    CurrencyController.delete = execute_transaction(LAYER.I_W_C_E.value)(
        CurrencyController.delete
    )
    CurrencyController.read = execute_transaction(LAYER.I_W_C_E.value)(
        CurrencyController.read
    )
