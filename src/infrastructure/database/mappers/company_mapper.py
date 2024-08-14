
from typing import List
from src.domain.models.entities.company.index import (
    Company,
    CompanySave,
    CompanyUpdate,
)
from src.infrastructure.database.entities.company_entity import CompanyEntity


def map_to_company(company_entity: CompanyEntity) -> Company:
    return Company(
        id=company_entity.id,
        name=company_entity.name,
        inactivity_time=company_entity.inactivity_time,
        nit=company_entity.nit,
        state=company_entity.state,
        created_date=company_entity.created_date,
        updated_date=company_entity.updated_date,
    )

def map_to_list_company(company_entities: List[CompanyEntity]) -> List[Company]:
    return [map_to_company(company) for company in company_entities]

def map_to_company_entity(company: Company) -> CompanyEntity:
    return CompanyEntity(
        id=company.id,
        name=company.name,
        inactivity_time=company.inactivity_time,
        nit=company.nit,
        state=company.state,
        created_date=company.created_date,
        updated_date=company.updated_date,
    )

def map_to_list_company_entity(companys: List[Company]) -> List[CompanyEntity]:
    return [map_to_company_entity(company) for company in companys]

def map_to_save_company_entity(company: CompanySave) -> CompanyEntity:
    return CompanyEntity(
        name=company.name,
        inactivity_time=company.inactivity_time,
        nit=company.nit,
        state=company.state,
    )

def map_to_update_company_entity(company: CompanyUpdate) -> CompanyEntity:
    return CompanyEntity(
        id=company.id,
        name=company.name,
        inactivity_time=company.inactivity_time,
        nit=company.nit,
        state=company.state,
    )

