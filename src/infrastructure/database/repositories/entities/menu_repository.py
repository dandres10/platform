
from pydantic import UUID4
from datetime import datetime
from typing import List, Union
from src.core.config import settings
from sqlalchemy.future import select
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.methods.get_filter import get_filter
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
    async def save(self, config: Config, params: MenuEntity) -> Union[Menu, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_menu(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: MenuUpdate) -> Union[Menu, None]:
        async with config.async_db as db:
            stmt = select(MenuEntity).filter(MenuEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            menu = result.scalars().first()

            if not menu:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(menu, key, value)

            await db.commit()
            await db.refresh(menu)
            return map_to_menu(menu)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Menu], None]:
        async with config.async_db as db:
            stmt = select(MenuEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=MenuEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            menus = result.scalars().all()

            if not menus:
                return None
            return map_to_list_menu(menus)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: MenuDelete,
    ) -> Union[Menu, None]:
        async with config.async_db as db:
            stmt = select(MenuEntity).filter(MenuEntity.id == params.id)
            result = await db.execute(stmt)
            menu = result.scalars().first()

            if not menu:
                return None

            await db.delete(menu)
            await db.commit()
            return map_to_menu(menu)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: MenuRead,
    ) -> Union[Menu, None]:
        async with config.async_db as db:
            stmt = select(MenuEntity).filter(MenuEntity.id == params.id)
            result = await db.execute(stmt)
            menu = result.scalars().first()

            if not menu:
                return None

            return map_to_menu(menu)
        