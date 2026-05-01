
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
from src.domain.models.entities.geo_division.index import (
    GeoDivision,
    GeoDivisionDelete,
    GeoDivisionRead,
    GeoDivisionSave,
    GeoDivisionUpdate,
)
from src.domain.services.repositories.entities.i_geo_division_repository import (
    IGeoDivisionRepository,
)
from src.infrastructure.database.entities.geo_division_entity import GeoDivisionEntity
from src.infrastructure.database.mappers.geo_division_mapper import (
    map_to_geo_division,
    map_to_list_geo_division,
    map_to_save_geo_division_entity,
)


class GeoDivisionRepository(IGeoDivisionRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: GeoDivisionSave) -> Union[GeoDivision, None]:
        db = config.async_db
        entity = map_to_save_geo_division_entity(params)
        db.add(entity)
        await db.commit()
        await db.refresh(entity)
        return map_to_geo_division(entity)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: GeoDivisionUpdate) -> Union[GeoDivision, None]:
        db = config.async_db
        stmt = select(GeoDivisionEntity).filter(GeoDivisionEntity.id == params.id)
        stmt.updated_date = datetime.now()
        result = await db.execute(stmt)
        geo_division = result.scalars().first()

        if not geo_division:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(geo_division, key, value)

        await db.commit()
        await db.refresh(geo_division)
        return map_to_geo_division(geo_division)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[GeoDivision], None]:
        db = config.async_db
        stmt = select(GeoDivisionEntity)

        if params.filters:
            stmt = get_filter(
                query=stmt, filters=params.filters, entity=GeoDivisionEntity
            )

        if not params.all_data:
            stmt = stmt.offset(params.skip).limit(params.limit)

        result = await db.execute(stmt)
        items = result.scalars().all()

        if not items:
            return None
        return map_to_list_geo_division(items)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: GeoDivisionDelete,
    ) -> Union[GeoDivision, None]:
        db = config.async_db
        stmt = select(GeoDivisionEntity).filter(GeoDivisionEntity.id == params.id)
        result = await db.execute(stmt)
        geo_division = result.scalars().first()

        if not geo_division:
            return None

        await db.delete(geo_division)
        await db.commit()
        return map_to_geo_division(geo_division)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: GeoDivisionRead,
    ) -> Union[GeoDivision, None]:
        db = config.async_db
        stmt = select(GeoDivisionEntity).filter(GeoDivisionEntity.id == params.id)
        result = await db.execute(stmt)
        geo_division = result.scalars().first()

        if not geo_division:
            return None

        return map_to_geo_division(geo_division)
