import uuid
from typing import Union, Dict, List, Tuple
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.enums.response_type import RESPONSE_TYPE
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from pydantic import UUID4

from src.domain.models.entities.menu.index import Menu, MenuSave
from src.domain.services.use_cases.entities.menu.menu_save_use_case import MenuSaveUseCase
from src.infrastructure.database.repositories.entities.menu_repository import MenuRepository

menu_repository = MenuRepository()


class CloneMenusForCompanyUseCase:
    
    def __init__(self):
        self.menu_save_uc = MenuSaveUseCase(menu_repository)
        self.message = Message()
    
    @execute_transaction(layer=LAYER.D_S_U_E.value, enabled=settings.has_track)
    async def execute(
        self,
        config: Config,
        company_id: UUID4,
        template_menus: List[Menu]
    ) -> Union[Tuple[List[Menu], Dict[str, str]], str]:
        config.response_type = RESPONSE_TYPE.OBJECT
        
        menu_mapping: Dict[str, str] = {}
        cloned_menus: List[Menu] = []
        
        for template_menu in template_menus:
            new_id = str(uuid.uuid4())
            menu_mapping[str(template_menu.id)] = new_id
        
        for template_menu in template_menus:
            new_id = menu_mapping[str(template_menu.id)]
            
            if str(template_menu.id) == str(template_menu.top_id):
                new_top_id = new_id
            else:
                new_top_id = menu_mapping[str(template_menu.top_id)]
            
            cloned_menu = await self.menu_save_uc.execute(
                config=config,
                params=MenuSave(
                    id=new_id,
                    company_id=company_id,
                    name=template_menu.name,
                    label=template_menu.label,
                    description=template_menu.description,
                    top_id=new_top_id,
                    route=template_menu.route,
                    state=template_menu.state,
                    icon=template_menu.icon
                )
            )
            
            if isinstance(cloned_menu, str):
                return await self.message.get_message(
                    config=config,
                    message=MessageCoreEntity(
                        key=KEYS_MESSAGES.CREATE_COMPANY_ERROR_CLONING_MENUS.value
                    ),
                )
            
            cloned_menus.append(cloned_menu)
        
        return (cloned_menus, menu_mapping)

