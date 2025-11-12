from typing import Union, Dict, List
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination, FilterManager
from src.core.enums.condition_type import CONDITION_TYPE
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity

from src.domain.models.entities.menu.index import Menu
from src.domain.models.entities.menu_permission.index import MenuPermissionSave
from src.domain.services.use_cases.entities.menu_permission.menu_permission_list_use_case import MenuPermissionListUseCase
from src.domain.services.use_cases.entities.menu_permission.menu_permission_save_use_case import MenuPermissionSaveUseCase
from src.infrastructure.database.repositories.entities.menu_permission_repository import MenuPermissionRepository

menu_permission_repository = MenuPermissionRepository()


class CloneMenuPermissionsForCompanyUseCase:
    
    def __init__(self):
        self.menu_permission_list_uc = MenuPermissionListUseCase(menu_permission_repository)
        self.menu_permission_save_uc = MenuPermissionSaveUseCase(menu_permission_repository)
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        cloned_menus: List[Menu],
        menu_mapping: Dict[str, str]
    ) -> Union[int, str]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        permissions_created = 0
        
        for cloned_menu in cloned_menus:
            original_menu_id = None
            for old_id, new_id in menu_mapping.items():
                if str(cloned_menu.id) == new_id:
                    original_menu_id = old_id
                    break
            
            if not original_menu_id:
                continue
            
            template_permissions = await self.menu_permission_list_uc.execute(
                config=config,
                params=Pagination(
                    filters=[
                        FilterManager(
                            field="menu_id",
                            value=original_menu_id,
                            condition=CONDITION_TYPE.EQUALS
                        )
                    ],
                    all_data=True
                )
            )
            
            if template_permissions and not isinstance(template_permissions, str):
                for template_permission in template_permissions:
                    cloned_permission = await self.menu_permission_save_uc.execute(
                        config=config,
                        params=MenuPermissionSave(
                            menu_id=cloned_menu.id,
                            permission_id=template_permission.permission_id,
                            state=template_permission.state
                        )
                    )
                    
                    if not isinstance(cloned_permission, str):
                        permissions_created += 1
        
        return permissions_created

