
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.language.index import Language, LanguageSave
from src.domain.services.repositories.entities.i_language_repository import (
    ILanguageRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.language_mapper import (
    map_to_save_language_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class LanguageSaveUseCase:
    def __init__(self, language_repository: ILanguageRepository):
        self.language_repository = language_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: LanguageSave,
    ) -> Union[Language, str, None]:
        result = map_to_save_language_entity(params)
        result = self.language_repository.save(config=config, params=result)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        result = result.dict()
        return result
        