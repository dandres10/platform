from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.language.index import (
    LanguageDelete,
    LanguageRead,
    LanguageSave,
    LanguageUpdate,
)
from src.domain.services.use_cases.entities.language.index import (
    LanguageDeleteUseCase,
    LanguageListUseCase,
    LanguageReadUseCase,
    LanguageSaveUseCase,
    LanguageUpdateUseCase,
)
from src.infrastructure.database.repositories.language_repository import (
    LanguageRepository,
)

language_repository = LanguageRepository()


class LanguageController:
    def __init__(self) -> None:
        self.language_save_use_case = LanguageSaveUseCase(language_repository)
        self.language_update_use_case = LanguageUpdateUseCase(language_repository)
        self.language_list_use_case = LanguageListUseCase(language_repository)
        self.language_delete_use_case = LanguageDeleteUseCase(language_repository)
        self.language_read_use_case = LanguageReadUseCase(language_repository)

    def save(self, config: Config, params: LanguageSave) -> Response:
        result_save = self.language_save_use_case.execute(config, params)
        if isinstance(result_save, str):
            return Response.error(None, result_save)
        return Response.success_temporary_message(
            response=result_save, message="Información guarda"
        )

    def update(self, config: Config, params: LanguageUpdate) -> Response:
        result_update = self.language_update_use_case.execute(config, params)
        if isinstance(result_update, str):
            return Response.error(None, result_update)
        return Response.success_temporary_message(
            response=result_update, message="Información actualizada"
        )

    def list(self, config: Config, params: Pagination) -> Response:
        result_list = self.language_list_use_case.execute(config, params)
        if isinstance(result_list, str):
            return Response.error(None, result_list)
        return Response.success_temporary_message(
            response=result_list, message="Consulta realizada"
        )

    def delete(self, config: Config, params: LanguageDelete) -> Response:
        result_delete = self.language_delete_use_case.execute(config, params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete, message="Eliminación realizada"
        )

    def read(self, config: Config, params: LanguageRead) -> Response:
        result_delete = self.language_read_use_case.execute(config, params)
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete, message="Consulta realizada"
        )


if settings.has_track:
    LanguageController.save = execute_transaction(LAYER.I_W_C_E.value)(
        LanguageController.save
    )
    LanguageController.update = execute_transaction(LAYER.I_W_C_E.value)(
        LanguageController.update
    )
    LanguageController.list = execute_transaction(LAYER.I_W_C_E.value)(
        LanguageController.list
    )
    LanguageController.delete = execute_transaction(LAYER.I_W_C_E.value)(
        LanguageController.delete
    )
    LanguageController.read = execute_transaction(LAYER.I_W_C_E.value)(
        LanguageController.read
    )
