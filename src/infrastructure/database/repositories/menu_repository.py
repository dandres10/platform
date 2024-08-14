
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.menu.index import (
    Menu,
    MenuDelete,
    MenuRead,
    MenuUpdate,
)
from src.domain.services.repositories.entities.i_menu_repository import (
    IMenuRepository,
)
from src.infrastructure.database.entities.menu_entity import MenuEntity
from src.infrastructure.database.mappers.menu_mapper import (
    map_to_menu,
    map_to_list_menu,
)


class MenuRepository(IMenuRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: MenuEntity) -> Union[Menu, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_menu(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: MenuUpdate) -> Union[Menu, None]:
        db = config.db

        menu: MenuEntity = (
            db.query(MenuEntity).filter(MenuEntity.id == params.id).first()
        )

        if not menu:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(menu, key, value)

        db.commit()
        db.refresh(menu)
        return map_to_menu(menu)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Menu], None]:
        db = config.db
        query = db.query(MenuEntity)

        if params.all_data:
            menus = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=MenuEntity
                )
                menus = query.offset(params.skip).limit(params.limit).all()

        if not menus:
            return None
        return map_to_list_menu(menus)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: MenuDelete,
    ) -> Union[Menu, None]:
        db = config.db
        menu: MenuEntity = (
            db.query(MenuEntity).filter(MenuEntity.id == params.id).first()
        )

        if not menu:
            return None

        db.delete(menu)
        db.commit()
        return map_to_menu(menu)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: MenuRead,
    ) -> Union[Menu, None]:
        db = config.db
        menu: MenuEntity = (
            db.query(MenuEntity).filter(MenuEntity.id == params.id).first()
        )

        if not menu:
            return None

        return map_to_menu(menu)
        