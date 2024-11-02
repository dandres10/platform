
from typing import List
from src.domain.models.entities.currency_location.index import (
    CurrencyLocation,
    CurrencyLocationSave,
    CurrencyLocationUpdate,
)
from src.infrastructure.database.entities.currency_location_entity import CurrencyLocationEntity


def map_to_currency_location(currency_location_entity: CurrencyLocationEntity) -> CurrencyLocation:
    return CurrencyLocation(
        id=currency_location_entity.id,
        currency_id=currency_location_entity.currency_id,
        location_id=currency_location_entity.location_id,
        state=currency_location_entity.state,
        created_date=currency_location_entity.created_date,
        updated_date=currency_location_entity.updated_date,
    )

def map_to_list_currency_location(currency_location_entities: List[CurrencyLocationEntity]) -> List[CurrencyLocation]:
    return [map_to_currency_location(currency_location) for currency_location in currency_location_entities]

def map_to_currency_location_entity(currency_location: CurrencyLocation) -> CurrencyLocationEntity:
    return CurrencyLocationEntity(
        id=currency_location.id,
        currency_id=currency_location.currency_id,
        location_id=currency_location.location_id,
        state=currency_location.state,
        created_date=currency_location.created_date,
        updated_date=currency_location.updated_date,
    )

def map_to_list_currency_location_entity(currency_locations: List[CurrencyLocation]) -> List[CurrencyLocationEntity]:
    return [map_to_currency_location_entity(currency_location) for currency_location in currency_locations]

def map_to_save_currency_location_entity(currency_location: CurrencyLocationSave) -> CurrencyLocationEntity:
    return CurrencyLocationEntity(
        currency_id=currency_location.currency_id,
        location_id=currency_location.location_id,
        state=currency_location.state,
    )

def map_to_update_currency_location_entity(currency_location: CurrencyLocationUpdate) -> CurrencyLocationEntity:
    return CurrencyLocationEntity(
        id=currency_location.id,
        currency_id=currency_location.currency_id,
        location_id=currency_location.location_id,
        state=currency_location.state,
    )

