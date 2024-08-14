
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.rol_permission.index import RolPermission, RolPermissionUpdate
from src.domain.services.repositories.entities.i_rol_permission_repository import (
    IRolPermissionRepository,
)
from src.core.config import settings
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class RolPermissionUpdateUseCase:
    def __init__(self, rol_permission_repository: IRolPermissionRepository):
        self.rol_permission_repository = rol_permission_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: RolPermissionUpdate,
    ) -> Union[RolPermission, str, None]:
        result = self.rol_permission_repository.update(config=config, params=params)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value),
            )

        if config.response_type == RESPONSE_TYPE.OBJECT.value:
            return result
        elif config.response_type == RESPONSE_TYPE.DICT.value:
            return result.dict() 

        return result
        