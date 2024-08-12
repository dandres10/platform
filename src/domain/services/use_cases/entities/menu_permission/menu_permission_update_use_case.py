
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.menu_permission.index import MenuPermission, MenuPermissionUpdate
from src.domain.services.repositories.entities.i_menu_permission_repository import (
    IMenuPermissionRepository,
)
from src.core.config import settings
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class MenuPermissionUpdateUseCase:
    def __init__(self, menu_permission_repository: IMenuPermissionRepository):
        self.menu_permission_repository = menu_permission_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: MenuPermissionUpdate,
    ) -> Union[MenuPermission, str, None]:
        result = self.menu_permission_repository.update(config=config, params=params)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value),
            )
        result = result.dict()
        return result
        