
from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.domain.models.entities.user_location.index import UserLocation
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.services.repositories.entities.i_user_location_repository import (
    IUserLocationRepository,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class UserLocationListUseCase:
    def __init__(self, user_location_repository: IUserLocationRepository):
        self.user_location_repository = user_location_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserLocation], str, None]:
        results = self.user_location_repository.list(config=config, params=params)
        if not results:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_NO_RESULTS_FOUND.value
                ),
            )
        results = [result.dict() for result in results]
        return results
        