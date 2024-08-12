
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.rol_permission.index import RolPermission, RolPermissionSave
from src.domain.services.repositories.entities.i_rol_permission_repository import (
    IRolPermissionRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.rol_permission_mapper import (
    map_to_save_rol_permission_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class RolPermissionSaveUseCase:
    def __init__(self, rol_permission_repository: IRolPermissionRepository):
        self.rol_permission_repository = rol_permission_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: RolPermissionSave,
    ) -> Union[RolPermission, str, None]:
        result = map_to_save_rol_permission_entity(params)
        result = self.rol_permission_repository.save(config=config, params=result)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_ERROR_SAVING_RECORD.value
                ),
            )
        result = result.dict()
        return result
        