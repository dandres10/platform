
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
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
    def save(self, config: Config, params: CurrencyEntity) -> Union[Currency, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_currency(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: CurrencyUpdate) -> Union[Currency, None]:
        db = config.db

        currency: CurrencyEntity = (
            db.query(CurrencyEntity).filter(CurrencyEntity.id == params.id).first()
        )

        if not currency:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(currency, key, value)

        db.commit()
        db.refresh(currency)
        return map_to_currency(currency)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Currency], None]:
        db = config.db
        query = db.query(CurrencyEntity)

        if params.all_data:
            currencys = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=CurrencyEntity
                )
                currencys = query.offset(params.skip).limit(params.limit).all()

        if not currencys:
            return None
        return map_to_list_currency(currencys)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: CurrencyDelete,
    ) -> Union[Currency, None]:
        db = config.db
        currency: CurrencyEntity = (
            db.query(CurrencyEntity).filter(CurrencyEntity.id == params.id).first()
        )

        if not currency:
            return None

        db.delete(currency)
        db.commit()
        return map_to_currency(currency)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: CurrencyRead,
    ) -> Union[Currency, None]:
        db = config.db
        currency: CurrencyEntity = (
            db.query(CurrencyEntity).filter(CurrencyEntity.id == params.id).first()
        )

        if not currency:
            return None

        return map_to_currency(currency)
        