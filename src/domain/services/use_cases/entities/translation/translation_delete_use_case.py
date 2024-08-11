from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.translation.index import TranslationDelete, Translation
from src.domain.services.repositories.entities.i_translation_repository import (
    ITranslationRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class TranslationDeleteUseCase:
    def __init__(self, translation_repository: ITranslationRepository):
        self.translation_repository = translation_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: TranslationDelete,
    ) -> Union[Translation, str, None]:
        result = self.translation_repository.delete(config=config, params=params)
        result = result.dict()
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        return result


