
from typing import List
from src.domain.models.entities.user_country.index import (
    UserCountry,
    UserCountrySave,
    UserCountryUpdate,
)
from src.infrastructure.database.entities.user_country_entity import UserCountryEntity


def map_to_user_country(user_country_entity: UserCountryEntity) -> UserCountry:
    return UserCountry(
        id=user_country_entity.id,
        user_id=user_country_entity.user_id,
        country_id=user_country_entity.country_id,
        state=user_country_entity.state,
        created_date=user_country_entity.created_date,
        updated_date=user_country_entity.updated_date,
    )

def map_to_list_user_country(user_country_entities: List[UserCountryEntity]) -> List[UserCountry]:
    return [map_to_user_country(user_country) for user_country in user_country_entities]

def map_to_user_country_entity(user_country: UserCountry) -> UserCountryEntity:
    return UserCountryEntity(
        id=user_country.id,
        user_id=user_country.user_id,
        country_id=user_country.country_id,
        state=user_country.state,
        created_date=user_country.created_date,
        updated_date=user_country.updated_date,
    )

def map_to_list_user_country_entity(user_countries: List[UserCountry]) -> List[UserCountryEntity]:
    return [map_to_user_country_entity(user_country) for user_country in user_countries]

def map_to_save_user_country_entity(user_country: UserCountrySave) -> UserCountryEntity:
    return UserCountryEntity(
        user_id=user_country.user_id,
        country_id=user_country.country_id,
        state=user_country.state,
    )

def map_to_update_user_country_entity(user_country: UserCountryUpdate) -> UserCountryEntity:
    return UserCountryEntity(
        id=user_country.id,
        user_id=user_country.user_id,
        country_id=user_country.country_id,
        state=user_country.state,
    )
