from typing import List, Union
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.domain.models.business.auth.login.auth_login_response import (
    LanguageLoginResponse,
    LocationLoginResponse,
)
from src.core.config import settings
from src.domain.services.use_cases.entities.language.language_list_use_case import (
    LanguageListUseCase,
)
from src.infrastructure.database.repositories.entities.language_repository import (
    LanguageRepository,
)

language_repository = LanguageRepository()


class AuthLanguagesUseCase:
    def __init__(
        self,
    ):
        self.language_list_use_case = LanguageListUseCase(
            language_repository=language_repository
        )
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(self, config: Config) -> Union[
        List[LocationLoginResponse],
        str,
    ]:

        results = await self.language_list_use_case.execute(
            config=config, params=Pagination(all_data=True)
        )

        if not results:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        # SPEC-019: response composition (Language DTO -> LanguageLoginResponse)
        return [
            LanguageLoginResponse(
                id=language.id,
                name=language.name,
                code=language.code,
                native_name=language.native_name,
                state=language.state,
            )
            for language in results
        ]
