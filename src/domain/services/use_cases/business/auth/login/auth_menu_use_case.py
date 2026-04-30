from typing import List, Union
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.login.auth_login_response import MenuLoginResponse
from src.domain.models.business.auth.login.auth_menu import AuthMenu
from src.domain.models.business.auth.login.menu import Menu
from src.infrastructure.database.repositories.business.auth_repository import (
    AuthRepository,
)
from src.core.config import settings
from src.core.classes.async_message import Message


class AuthMenuUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()
        self.message = Message()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        params: AuthMenu,
    ) -> Union[List[MenuLoginResponse], str]:
        config.response_type = RESPONSE_TYPE.OBJECT

        if not params.company:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_REQUIRED_FIELD.value
                ),
            )

        result = await self.auth_repository.menu(
            config=config,
            params=Menu(company=params.company),
        )

        if not result:
            return await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        # SPEC-015 T5
        menu_permissions, menus = result
        permission_ids = {permission.id for permission in params.permissions}
        allowed_menu_ids = {
            mp.menu_id for mp in menu_permissions if mp.permission_id in permission_ids
        }
        return [menu for menu in menus if menu.id in allowed_menu_ids]
