from typing import List, Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction

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

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: Pagination,
    ) -> Union[List[UserByLocationItem], None]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        users = await self.auth_repository.users_internal(
            config=config,
            params=params
        )
        
        return users

