
from typing import List
from src.domain.models.entities.menu.index import (
    Menu,
    MenuSave,
    MenuUpdate,
)
from src.infrastructure.database.entities.menu_entity import MenuEntity


def map_to_menu(menu_entity: MenuEntity) -> Menu:
    return Menu(
        id=menu_entity.id,
        company_id=menu_entity.company_id,
        name=menu_entity.name,
        description=menu_entity.description,
        top_id=menu_entity.top_id,
        route=menu_entity.route,
        state=menu_entity.state,
        icon=menu_entity.icon,
        created_date=menu_entity.created_date,
        updated_date=menu_entity.updated_date,
    )

def map_to_list_menu(menu_entities: List[MenuEntity]) -> List[Menu]:
    return [map_to_menu(menu) for menu in menu_entities]

def map_to_menu_entity(menu: Menu) -> MenuEntity:
    return MenuEntity(
        id=menu.id,
        company_id=menu.company_id,
        name=menu.name,
        description=menu.description,
        top_id=menu.top_id,
        route=menu.route,
        state=menu.state,
        icon=menu.icon,
        created_date=menu.created_date,
        updated_date=menu.updated_date,
    )

def map_to_list_menu_entity(menus: List[Menu]) -> List[MenuEntity]:
    return [map_to_menu_entity(menu) for menu in menus]

def map_to_save_menu_entity(menu: MenuSave) -> MenuEntity:
    return MenuEntity(
        company_id=menu.company_id,
        name=menu.name,
        description=menu.description,
        top_id=menu.top_id,
        route=menu.route,
        state=menu.state,
        icon=menu.icon,
    )

def map_to_update_menu_entity(menu: MenuUpdate) -> MenuEntity:
    return MenuEntity(
        id=menu.id,
        company_id=menu.company_id,
        name=menu.name,
        description=menu.description,
        top_id=menu.top_id,
        route=menu.route,
        state=menu.state,
        icon=menu.icon,
    )

