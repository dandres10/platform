from typing import Union
from src.core.classes.password import Password
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user.index import User, UserSave
from src.domain.services.repositories.entities.i_user_repository import (
    IUserRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.user_mapper import (
    map_to_save_user_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class UserSaveUseCase:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository
        self.message = Message()
        self.password = Password()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: UserSave,
    ) -> Union[User, str, None]:
        result = map_to_save_user_entity(params)
        result.password = self.password.hash_password(password=result.password)
        result = self.user_repository.save(config=config, params=result)

        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )

        if params.dict_number == "all":
            return result
        elif params.dict_number == "dict":
            return result.dict()
        elif params.dict_number == "dict1":
            return result.dict1()
        return result
