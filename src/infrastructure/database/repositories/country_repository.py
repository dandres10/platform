
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
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
    def save(self, config: Config, params: CountryEntity) -> Union[Country, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_country(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: CountryUpdate) -> Union[Country, None]:
        db = config.db

        country: CountryEntity = (
            db.query(CountryEntity).filter(CountryEntity.id == params.id).first()
        )

        if not country:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(country, key, value)

        db.commit()
        db.refresh(country)
        return map_to_country(country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Country], None]:
        db = config.db
        query = db.query(CountryEntity)

        if params.all_data:
            countrys = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=CountryEntity
                )
                countrys = query.offset(params.skip).limit(params.limit).all()

        if not countrys:
            return None
        return map_to_list_country(countrys)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: CountryDelete,
    ) -> Union[Country, None]:
        db = config.db
        country: CountryEntity = (
            db.query(CountryEntity).filter(CountryEntity.id == params.id).first()
        )

        if not country:
            return None

        db.delete(country)
        db.commit()
        return map_to_country(country)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: CountryRead,
    ) -> Union[Country, None]:
        db = config.db
        country: CountryEntity = (
            db.query(CountryEntity).filter(CountryEntity.id == params.id).first()
        )

        if not country:
            return None

        return map_to_country(country)
        