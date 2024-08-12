
from typing import Union
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.menu.index import Menu, MenuUpdate
from src.domain.services.repositories.entities.i_menu_repository import (
    IMenuRepository,
)
from src.core.config import settings
from src.core.classes.message import Message
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.message import MessageCoreEntity


class MenuUpdateUseCase:
    def __init__(self, menu_repository: IMenuRepository):
        self.menu_repository = menu_repository
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: MenuUpdate,
    ) -> Union[Menu, str, None]:
        result = self.menu_repository.update(config=config, params=params)
        if not result:
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_UPDATE_FAILED.value),
            )
        result = result.dict()
        return result
        