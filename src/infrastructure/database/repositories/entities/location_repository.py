
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
from src.domain.models.entities.location.index import (
    Location,
    LocationDelete,
    LocationRead,
    LocationUpdate,
)
from src.domain.services.repositories.entities.i_location_repository import (
    ILocationRepository,
)
from src.infrastructure.database.entities.location_entity import LocationEntity
from src.infrastructure.database.mappers.location_mapper import (
    map_to_location,
    map_to_list_location,
)


class LocationRepository(ILocationRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: LocationEntity) -> Union[Location, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_location(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: LocationUpdate) -> Union[Location, None]:
        async with config.async_db as db:
            stmt = select(LocationEntity).filter(LocationEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            location = result.scalars().first()

            if not location:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(location, key, value)

            await db.commit()
            await db.refresh(location)
            return map_to_location(location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Location], None]:
        async with config.async_db as db:
            stmt = select(LocationEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=LocationEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            locations = result.scalars().all()

            if not locations:
                return None
            return map_to_list_location(locations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: LocationDelete,
    ) -> Union[Location, None]:
        async with config.async_db as db:
            stmt = select(LocationEntity).filter(LocationEntity.id == params.id)
            result = await db.execute(stmt)
            location = result.scalars().first()

            if not location:
                return None

            await db.delete(location)
            await db.commit()
            return map_to_location(location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: LocationRead,
    ) -> Union[Location, None]:
        async with config.async_db as db:
            stmt = select(LocationEntity).filter(LocationEntity.id == params.id)
            result = await db.execute(stmt)
            location = result.scalars().first()

            if not location:
                return None

            return map_to_location(location)
        