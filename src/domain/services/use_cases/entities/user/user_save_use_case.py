
from typing import Union
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.classes.password import Password
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user.index import User, UserSave
from src.domain.services.repositories.entities.i_user_repository import (
    IUserRepository,
)
from src.infrastructure.database.mappers.user_mapper import (
    map_to_save_user_entity,
)


class UserSaveUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        self.message = Message()
        self.password = Password()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: UserSave,
    ) -> Union[User, str, None]:
        result = map_to_save_user_entity(params)
        result.password = self.password.hash_password(password=result.password)
        result = await self.user_repository.save(config=config, params=result)
        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict() 

        return result
        