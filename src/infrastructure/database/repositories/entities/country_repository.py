
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
from src.domain.models.entities.country.index import (
    Country,
    CountryDelete,
    CountryRead,
    CountryUpdate,
)
from src.domain.services.repositories.entities.i_country_repository import (
    ICountryRepository,
)
from src.infrastructure.database.entities.country_entity import CountryEntity
from src.infrastructure.database.mappers.country_mapper import (
    map_to_country,
    map_to_list_country,
)


class CountryRepository(ICountryRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: CountryEntity) -> Union[Country, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_country(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: CountryUpdate) -> Union[Country, None]:
        async with config.async_db as db:
            stmt = select(CountryEntity).filter(CountryEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            country = result.scalars().first()

            if not country:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(country, key, value)

            await db.commit()
            await db.refresh(country)
            return map_to_country(country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Country], None]:
        async with config.async_db as db:
            stmt = select(CountryEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=CountryEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            countrys = result.scalars().all()

            if not countrys:
                return None
            return map_to_list_country(countrys)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: CountryDelete,
    ) -> Union[Country, None]:
        async with config.async_db as db:
            stmt = select(CountryEntity).filter(CountryEntity.id == params.id)
            result = await db.execute(stmt)
            country = result.scalars().first()

            if not country:
                return None

            await db.delete(country)
            await db.commit()
            return map_to_country(country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: CountryRead,
    ) -> Union[Country, None]:
        async with config.async_db as db:
            stmt = select(CountryEntity).filter(CountryEntity.id == params.id)
            result = await db.execute(stmt)
            country = result.scalars().first()

            if not country:
                return None

            return map_to_country(country)
        