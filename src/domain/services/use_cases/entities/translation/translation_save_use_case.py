from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.translation.index import Translation, TranslationSave
from src.domain.services.repositories.entities.i_translation_repository import (
    ITranslationRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.translation_mapper import (
    map_to_save_translation_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class TranslationSaveUseCase:
    def __init__(self, translation_repository: ITranslationRepository):
        self.translation_repository = translation_repository
        self.message = Message()

    def execute(
        self,
        config: Config,
        params: TranslationSave,
    ) -> Union[Translation, str, None]:
        result = map_to_save_translation_entity(params)
        result = self.translation_repository.save(config=config, params=result)
        result = result.dict()
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        return result


if settings.has_track:
    TranslationSaveUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        TranslationSaveUseCase.execute
    )
