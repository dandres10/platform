from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.response import Response
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.translation.index import (
    TranslationDelete,
    TranslationRead,
    TranslationSave,
    TranslationUpdate,
)
from src.domain.services.use_cases.entities.translation.index import (
    TranslationDeleteUseCase,
    TranslationListUseCase,
    TranslationReadUseCase,
    TranslationSaveUseCase,
    TranslationUpdateUseCase,
)
from src.infrastructure.database.repositories.translation_repository import (
    TranslationRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

translation_repository = TranslationRepository()


class TranslationController:
    def __init__(self) -> None:
        self.translation_save_use_case = TranslationSaveUseCase(translation_repository)
        self.translation_update_use_case = TranslationUpdateUseCase(
            translation_repository
        )
        self.translation_list_use_case = TranslationListUseCase(translation_repository)
        self.translation_delete_use_case = TranslationDeleteUseCase(
            translation_repository
        )
        self.translation_read_use_case = TranslationReadUseCase(translation_repository)
        self.message = Message()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    def save(self, config: Config, params: TranslationSave) -> Response:
        result_save = self.translation_save_use_case.execute(
            config=config, params=params
        )
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
    def update(self, config: Config, params: TranslationUpdate) -> Response:
        result_update = self.translation_update_use_case.execute(
            config=config, params=params
        )
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
        result_list = self.translation_list_use_case.execute(
            config=config, params=params
        )
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
    def delete(self, config: Config, params: TranslationDelete) -> Response:
        result_delete = self.translation_delete_use_case.execute(
            config=config, params=params
        )
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
    def read(self, config: Config, params: TranslationRead) -> Response:
        result_delete = self.translation_read_use_case.execute(
            config=config, params=params
        )
        if isinstance(result_delete, str):
            return Response.error(None, result_delete)
        return Response.success_temporary_message(
            response=result_delete,
            message=self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
