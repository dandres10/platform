from typing import List, Union
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_locations import AuthLocations
from src.domain.models.business.auth.login.auth_login_response import (
    LocationLoginResponse,
)
from src.core.config import settings
from src.domain.services.use_cases.entities.language.language_list_use_case import (
    LanguageListUseCase,
)
from src.infrastructure.database.repositories.business.mappers.auth.login.login_mapper import (
    map_to_language_base_response,
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

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(self, config: Config) -> Union[
        List[LocationLoginResponse],
        str,
    ]:

        results = self.language_list_use_case.execute(
            config=config, params=Pagination(all_data=True)
        )

        if not results:
            print("no se encontraron idiomas")
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        results = [map_to_language_base_response(result) for result in results]

        return results
