
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.user_location_rol.index import UserLocationRol, UserLocationRolSave
from src.domain.services.repositories.entities.i_user_location_rol_repository import (
    IUserLocationRolRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.user_location_rol_mapper import (
    map_to_save_user_location_rol_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class UserLocationRolSaveUseCase:
    def __init__(self, user_location_rol_repository: IUserLocationRolRepository):
        self.user_location_rol_repository = user_location_rol_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: UserLocationRolSave,
    ) -> Union[UserLocationRol, str, None]:
        result = map_to_save_user_location_rol_entity(params)
        result = self.user_location_rol_repository.save(config=config, params=result)
        if not result:
            return self.message.get_message(
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
        