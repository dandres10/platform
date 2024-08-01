from typing import List
from src.domain.models.entities.currency.currency import Currency
from src.domain.models.entities.currency.currency_save import CurrencySave
from src.domain.models.entities.currency.currency_update import CurrencyUpdate
from src.infrastructure.database.entities.currency_entity import CurrencyEntity


def map_to_currency(currency_entity: CurrencyEntity) -> Currency:
    return Currency(
        id=currency_entity.id,
        name=currency_entity.name,
        code=currency_entity.code,
        symbol=currency_entity.symbol,
        state=currency_entity.state,
        created_date=currency_entity.created_date,
        updated_date=currency_entity.updated_date,
    )


def map_to_list_currency(currency_entities: List[CurrencyEntity]) -> List[Currency]:
    return [map_to_currency(currency) for currency in currency_entities]


def map_to_currency_entity(currency: Currency) -> CurrencyEntity:
    return CurrencyEntity(
        id=currency.id,
        name=currency.name,
        code=currency.code,
        symbol=currency.symbol,
        state=currency.state,
        created_date=currency.created_date,
        updated_date=currency.updated_date,
    )


def map_to_list_currency_entity(currencys: List[Currency]) -> List[CurrencyEntity]:
    return [map_to_currency_entity(currency) for currency in currencys]


def map_to_save_currency_entity(currency: CurrencySave) -> CurrencyEntity:
    return CurrencyEntity(
        name=currency.name,
        code=currency.code,
        symbol=currency.symbol,
        state=currency.state,
    )


def map_to_update_currency_entity(currency: CurrencyUpdate) -> CurrencyEntity:
    return CurrencyEntity(
        id=currency.id,
        name=currency.name,
        code=currency.code,
        native_name=currency.native_name,
        state=currency.state,
    )
