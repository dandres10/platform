from typing import List, Union
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.enums.layer import LAYER
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.models.config import Config
from src.core.models.message import MessageCoreEntity
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.auth.auth_login_response import MenuLoginResponse
from src.domain.models.business.auth.auth_menu import AuthMenu
from src.domain.models.business.auth.menu import Menu
from src.infrastructure.database.entities.menu_entity import MenuEntity
from src.infrastructure.database.entities.menu_permission_entity import MenuPermissionEntity
from src.infrastructure.database.repositories.business.auth_repository import AuthRepository
from src.core.config import settings
from src.infrastructure.database.repositories.business.mappers.auth_mapper import map_to_menu_response

class AuthMenuUseCase:
    def __init__(
        self,
    ):
        self.auth_repository = AuthRepository()

    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    def execute(
        self,
        config: Config,
        params: AuthMenu,
    ) -> Union[
        List[MenuLoginResponse],
        str,
    ]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        menus = self.auth_repository.menu(
            config=config,
            params=Menu(company=params.company),
        )

        if not menus:
            print("no se encontro el menu de la empresa")
            return self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_RECORD_NOT_FOUND_TO_DELETE.value
                ),
            )

        list_menu_permission_entity: List[MenuPermissionEntity] = []
        list_menu_entity: List[MenuEntity] = []

        for menu in menus:
            menu_permission_entity, menu_entity = menu
            list_menu_permission_entity.append(menu_permission_entity)
            list_menu_entity.append(menu_entity)

        permission_ids = {permission.id for permission in params.permissions}
        menu_permissions = [
            menu_permission
            for menu_permission in list_menu_permission_entity
            if menu_permission.permission_id in permission_ids
        ]

        menu_ids = {menu_permission.menu_id for menu_permission in menu_permissions}

        result = [
            map_to_menu_response(menu_entity=menuu)
            for menuu in list_menu_entity
            if menuu.id in menu_ids
        ]
        


        return result