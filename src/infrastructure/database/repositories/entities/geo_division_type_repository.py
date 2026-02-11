
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
from src.domain.models.entities.geo_division_type.index import (
    GeoDivisionType,
    GeoDivisionTypeDelete,
    GeoDivisionTypeRead,
    GeoDivisionTypeUpdate,
)
from src.domain.services.repositories.entities.i_geo_division_type_repository import (
    IGeoDivisionTypeRepository,
)
from src.infrastructure.database.entities.geo_division_type_entity import GeoDivisionTypeEntity
from src.infrastructure.database.mappers.geo_division_type_mapper import (
    map_to_geo_division_type,
    map_to_list_geo_division_type,
)


class GeoDivisionTypeRepository(IGeoDivisionTypeRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: GeoDivisionTypeEntity) -> Union[GeoDivisionType, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_geo_division_type(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: GeoDivisionTypeUpdate) -> Union[GeoDivisionType, None]:
        async with config.async_db as db:
            stmt = select(GeoDivisionTypeEntity).filter(GeoDivisionTypeEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            geo_division_type = result.scalars().first()

            if not geo_division_type:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(geo_division_type, key, value)

            await db.commit()
            await db.refresh(geo_division_type)
            return map_to_geo_division_type(geo_division_type)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[GeoDivisionType], None]:
        async with config.async_db as db:
            stmt = select(GeoDivisionTypeEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=GeoDivisionTypeEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            items = result.scalars().all()

            if not items:
                return None
            return map_to_list_geo_division_type(items)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: GeoDivisionTypeDelete,
    ) -> Union[GeoDivisionType, None]:
        async with config.async_db as db:
            stmt = select(GeoDivisionTypeEntity).filter(GeoDivisionTypeEntity.id == params.id)
            result = await db.execute(stmt)
            geo_division_type = result.scalars().first()

            if not geo_division_type:
                return None

            await db.delete(geo_division_type)
            await db.commit()
            return map_to_geo_division_type(geo_division_type)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: GeoDivisionTypeRead,
    ) -> Union[GeoDivisionType, None]:
        async with config.async_db as db:
            stmt = select(GeoDivisionTypeEntity).filter(GeoDivisionTypeEntity.id == params.id)
            result = await db.execute(stmt)
            geo_division_type = result.scalars().first()

            if not geo_division_type:
                return None

            return map_to_geo_division_type(geo_division_type)
