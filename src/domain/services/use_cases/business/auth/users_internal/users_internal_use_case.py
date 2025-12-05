from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.business.auth.list_users_by_location import (
    UserByLocationItem
)

from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository
)


auth_repository = AuthRepository()


class UsersInternalUseCase:
    def __init__(self):
        self.auth_repository = auth_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserByLocationItem], str, None]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        # Validar que el filtro location_id esté presente y coincida con el del token
        location_id_filter = None
        
        if params.filters:
            for filter_item in params.filters:
                if filter_item.field == "location_id":
                    location_id_filter = filter_item.value
                    break
        
        # Si no se envió filtro de location_id, retornar error
        if not location_id_filter:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_USERS_INTERNAL_LOCATION_REQUIRED.value
                ),
            )
        
        # Validar que el location_id del filtro coincida con el del token
        admin_location_id = str(config.token.location_id)
        
        if str(location_id_filter) != admin_location_id:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.AUTH_USERS_INTERNAL_LOCATION_MISMATCH.value
                ),
            )
        
        users = await self.auth_repository.users_internal(
            config=config,
            params=params
        )
        
        return users

