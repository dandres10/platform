
from typing import List
from src.domain.models.entities.company_currency.index import (
    CompanyCurrency,
    CompanyCurrencySave,
    CompanyCurrencyUpdate,
)
from src.infrastructure.database.entities.company_currency_entity import CompanyCurrencyEntity


def map_to_company_currency(company_currency_entity: CompanyCurrencyEntity) -> CompanyCurrency:
    return CompanyCurrency(
        id=company_currency_entity.id,
        company_id=company_currency_entity.company_id,
        currency_id=company_currency_entity.currency_id,
        is_base=company_currency_entity.is_base,
        state=company_currency_entity.state,
        created_date=company_currency_entity.created_date,
        updated_date=company_currency_entity.updated_date,
    )

def map_to_list_company_currency(company_currency_entities: List[CompanyCurrencyEntity]) -> List[CompanyCurrency]:
    return [map_to_company_currency(company_currency) for company_currency in company_currency_entities]

def map_to_company_currency_entity(company_currency: CompanyCurrency) -> CompanyCurrencyEntity:
    return CompanyCurrencyEntity(
        id=company_currency.id,
        company_id=company_currency.company_id,
        currency_id=company_currency.currency_id,
        is_base=company_currency.is_base,
        state=company_currency.state,
        created_date=company_currency.created_date,
        updated_date=company_currency.updated_date,
    )

def map_to_list_company_currency_entity(company_currencies: List[CompanyCurrency]) -> List[CompanyCurrencyEntity]:
    return [map_to_company_currency_entity(company_currency) for company_currency in company_currencies]

def map_to_save_company_currency_entity(company_currency: CompanyCurrencySave) -> CompanyCurrencyEntity:
    return CompanyCurrencyEntity(
        company_id=company_currency.company_id,
        currency_id=company_currency.currency_id,
        is_base=company_currency.is_base,
        state=company_currency.state,
    )

def map_to_update_company_currency_entity(company_currency: CompanyCurrencyUpdate) -> CompanyCurrencyEntity:
    return CompanyCurrencyEntity(
        id=company_currency.id,
        currency_id=company_currency.currency_id,
        is_base=company_currency.is_base,
        state=company_currency.state,
    )

