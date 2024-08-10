from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.domain.models.entities.translation.index import Translation
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.services.repositories.entities.i_translation_repository import (
    ITranslationRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class TranslationListUseCase:
    def __init__(self, translation_repository: ITranslationRepository):
        self.translation_repository = translation_repository
        self.message = Message()

    def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[Translation], str, None]:
        results = self.translation_repository.list(config=config, params=params)
        results = [result.dict() for result in results]
        if not results:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )
        return results


if settings.has_track:
    TranslationListUseCase.execute = execute_transaction(LAYER.D_S_U_E.value)(
        TranslationListUseCase.execute
    )
