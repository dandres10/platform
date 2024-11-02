
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
from src.domain.models.entities.currency_location.index import (
    CurrencyLocation,
    CurrencyLocationDelete,
    CurrencyLocationRead,
    CurrencyLocationUpdate,
)
from src.domain.services.repositories.entities.i_currency_location_repository import (
    ICurrencyLocationRepository,
)
from src.infrastructure.database.entities.currency_location_entity import CurrencyLocationEntity
from src.infrastructure.database.mappers.currency_location_mapper import (
    map_to_currency_location,
    map_to_list_currency_location,
)


class CurrencyLocationRepository(ICurrencyLocationRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: CurrencyLocationEntity) -> Union[CurrencyLocation, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_currency_location(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: CurrencyLocationUpdate) -> Union[CurrencyLocation, None]:
        async with config.async_db as db:
            stmt = select(CurrencyLocationEntity).filter(CurrencyLocationEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            currency_location = result.scalars().first()

            if not currency_location:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(currency_location, key, value)

            await db.commit()
            await db.refresh(currency_location)
            return map_to_currency_location(currency_location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[CurrencyLocation], None]:
        async with config.async_db as db:
            stmt = select(CurrencyLocationEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=CurrencyLocationEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            currency_locations = result.scalars().all()

            if not currency_locations:
                return None
            return map_to_list_currency_location(currency_locations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: CurrencyLocationDelete,
    ) -> Union[CurrencyLocation, None]:
        async with config.async_db as db:
            stmt = select(CurrencyLocationEntity).filter(CurrencyLocationEntity.id == params.id)
            result = await db.execute(stmt)
            currency_location = result.scalars().first()

            if not currency_location:
                return None

            await db.delete(currency_location)
            await db.commit()
            return map_to_currency_location(currency_location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: CurrencyLocationRead,
    ) -> Union[CurrencyLocation, None]:
        async with config.async_db as db:
            stmt = select(CurrencyLocationEntity).filter(CurrencyLocationEntity.id == params.id)
            result = await db.execute(stmt)
            currency_location = result.scalars().first()

            if not currency_location:
                return None

            return map_to_currency_location(currency_location)
        