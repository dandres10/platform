
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
from src.domain.models.entities.currency.index import (
    Currency,
    CurrencyDelete,
    CurrencyRead,
    CurrencyUpdate,
)
from src.domain.services.repositories.entities.i_currency_repository import (
    ICurrencyRepository,
)
from src.infrastructure.database.entities.currency_entity import CurrencyEntity
from src.infrastructure.database.mappers.currency_mapper import (
    map_to_currency,
    map_to_list_currency,
)


class CurrencyRepository(ICurrencyRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def save(self, config: Config, params: CurrencyEntity) -> Union[Currency, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_currency(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: CurrencyUpdate) -> Union[Currency, None]:
        async with config.async_db as db:
            stmt = select(CurrencyEntity).filter(CurrencyEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            currency = result.scalars().first()

            if not currency:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(currency, key, value)

            await db.commit()
            await db.refresh(currency)
            return map_to_currency(currency)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Currency], None]:
        async with config.async_db as db:
            stmt = select(CurrencyEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=CurrencyEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            currencys = result.scalars().all()

            if not currencys:
                return None
            return map_to_list_currency(currencys)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: CurrencyDelete,
    ) -> Union[Currency, None]:
        async with config.async_db as db:
            stmt = select(CurrencyEntity).filter(CurrencyEntity.id == params.id)
            result = await db.execute(stmt)
            currency = result.scalars().first()

            if not currency:
                return None

            await db.delete(currency)
            await db.commit()
            return map_to_currency(currency)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: CurrencyRead,
    ) -> Union[Currency, None]:
        async with config.async_db as db:
            stmt = select(CurrencyEntity).filter(CurrencyEntity.id == params.id)
            result = await db.execute(stmt)
            currency = result.scalars().first()

            if not currency:
                return None

            return map_to_currency(currency)
        