
from typing import List
from src.domain.models.entities.country.index import (
    Country,
    CountrySave,
    CountryUpdate,
)
from src.infrastructure.database.entities.country_entity import CountryEntity


def map_to_country(country_entity: CountryEntity) -> Country:
    return Country(
        id=country_entity.id,
        name=country_entity.name,
        code=country_entity.code,
        phone_code=country_entity.phone_code,
        state=country_entity.state,
        created_date=country_entity.created_date,
        updated_date=country_entity.updated_date,
    )

def map_to_list_country(country_entities: List[CountryEntity]) -> List[Country]:
    return [map_to_country(country) for country in country_entities]

def map_to_country_entity(country: Country) -> CountryEntity:
    return CountryEntity(
        id=country.id,
        name=country.name,
        code=country.code,
        phone_code=country.phone_code,
        state=country.state,
        created_date=country.created_date,
        updated_date=country.updated_date,
    )

def map_to_list_country_entity(countrys: List[Country]) -> List[CountryEntity]:
    return [map_to_country_entity(country) for country in countrys]

def map_to_save_country_entity(country: CountrySave) -> CountryEntity:
    return CountryEntity(
        name=country.name,
        code=country.code,
        phone_code=country.phone_code,
        state=country.state,
    )

def map_to_update_country_entity(country: CountryUpdate) -> CountryEntity:
    return CountryEntity(
        id=country.id,
        name=country.name,
        code=country.code,
        phone_code=country.phone_code,
        state=country.state,
    )

