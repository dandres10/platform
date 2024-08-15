
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.menu_permission.index import MenuPermission, MenuPermissionSave
from src.domain.services.repositories.entities.i_menu_permission_repository import (
    IMenuPermissionRepository,
)
from src.core.config import settings
from src.infrastructure.database.mappers.menu_permission_mapper import (
    map_to_save_menu_permission_entity,
)
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity

class MenuPermissionSaveUseCase:
    def __init__(self, menu_permission_repository: IMenuPermissionRepository):
        self.menu_permission_repository = menu_permission_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: MenuPermissionSave,
    ) -> Union[MenuPermission, str, None]:
        result = map_to_save_menu_permission_entity(params)
        result = self.menu_permission_repository.save(config=config, params=result)
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
        