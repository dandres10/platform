
from typing import List, Union
from pydantic import UUID4
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.methods.get_filter import get_filter
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.entities.company.index import (
    Company,
    CompanyDelete,
    CompanyRead,
    CompanyUpdate,
)
from src.domain.services.repositories.entities.i_company_repository import (
    ICompanyRepository,
)
from src.infrastructure.database.entities.company_entity import CompanyEntity
from src.infrastructure.database.mappers.company_mapper import (
    map_to_company,
    map_to_list_company,
)


class CompanyRepository(ICompanyRepository):

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def save(self, config: Config, params: CompanyEntity) -> Union[Company, None]:
        db = config.db
        db.add(params)
        db.commit()
        db.refresh(params)
        return map_to_company(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def update(self, config: Config, params: CompanyUpdate) -> Union[Company, None]:
        db = config.db

        company: CompanyEntity = (
            db.query(CompanyEntity).filter(CompanyEntity.id == params.id).first()
        )

        if not company:
            return None

        update_data = params.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(company, key, value)

        db.commit()
        db.refresh(company)
        return map_to_company(company)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def list(self, config: Config, params: Pagination) -> Union[List[Company], None]:
        db = config.db
        query = db.query(CompanyEntity)

        if params.all_data:
            companys = query.all()
        else:
            if params.filters:
                query = get_filter(
                    query=query, filters=params.filters, entity=CompanyEntity
                )
                companys = query.offset(params.skip).limit(params.limit).all()

        if not companys:
            return None
        return map_to_list_company(companys)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def delete(
        self,
        config: Config,
        params: CompanyDelete,
    ) -> Union[Company, None]:
        db = config.db
        company: CompanyEntity = (
            db.query(CompanyEntity).filter(CompanyEntity.id == params.id).first()
        )

        if not company:
            return None

        db.delete(company)
        db.commit()
        return map_to_company(company)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    def read(
        self,
        config: Config,
        params: CompanyRead,
    ) -> Union[Company, None]:
        db = config.db
        company: CompanyEntity = (
            db.query(CompanyEntity).filter(CompanyEntity.id == params.id).first()
        )

        if not company:
            return None

        return map_to_company(company)
        