from typing import List, Union
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.auth_locations import AuthLocations
from src.domain.models.business.auth.auth_login_response import CurrecyLoginResponse, LocationLoginResponse
from src.core.config import settings
from src.infrastructure.database.mappers.currency_mapper import map_to_list_currency
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.infrastructure.database.repositories.business.mappers.auth_mapper import (
    map_to_currecy_login_response,
    map_to_location_login_response,
)


class AuthLocationsUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(self, config: Config, params: AuthLocations) -> Union[
        List[LocationLoginResponse],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT
        locations: List[LocationLoginResponse] = []

        results = self.auth_repository.locations_by_user(
            config=config, params=params
        )

        if not results:
            print("no se encontraron locations")
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        for result in results:
            user_location_rol_entity, location_entity, company_entity, user_entity = result
            locations.append(map_to_location_login_response(location_entity=location_entity))


        return locations
