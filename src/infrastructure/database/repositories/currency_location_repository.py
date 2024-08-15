
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
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
    def save(self, config: Config, params: CurrencyLocationEntity) -> Union[CurrencyLocation, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_currency_location(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: CurrencyLocationUpdate) -> Union[CurrencyLocation, None]:
        db = config.db

        currency_location: CurrencyLocationEntity = (
            db.query(CurrencyLocationEntity).filter(CurrencyLocationEntity.id == params.id).first()
        )

        if not currency_location:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(currency_location, key, value)

        db.commit()
        db.refresh(currency_location)
        return map_to_currency_location(currency_location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[CurrencyLocation], None]:
        db = config.db
        query = db.query(CurrencyLocationEntity)

        if params.all_data:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=CurrencyLocationEntity
                )
                currency_locations = query.all()
            else:
                currency_locations = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=CurrencyLocationEntity
                )
                currency_locations = query.offset(params.skip).limit(params.limit).all()

        if not currency_locations:
            return None
        return map_to_list_currency_location(currency_locations)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: CurrencyLocationDelete,
    ) -> Union[CurrencyLocation, None]:
        db = config.db
        currency_location: CurrencyLocationEntity = (
            db.query(CurrencyLocationEntity).filter(CurrencyLocationEntity.id == params.id).first()
        )

        if not currency_location:
            return None

        db.delete(currency_location)
        db.commit()
        return map_to_currency_location(currency_location)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: CurrencyLocationRead,
    ) -> Union[CurrencyLocation, None]:
        db = config.db
        currency_location: CurrencyLocationEntity = (
            db.query(CurrencyLocationEntity).filter(CurrencyLocationEntity.id == params.id).first()
        )

        if not currency_location:
            return None

        return map_to_currency_location(currency_location)
        