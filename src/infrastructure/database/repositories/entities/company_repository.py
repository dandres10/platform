
from pydantic import UUID4
from datetime import datetime
from typing import List, Union
from src.core.config import settings
from sqlalchemy.future import select
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.filter import Pagination
from src.core.methods.get_filter import get_filter
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
    async def save(self, config: Config, params: CompanyEntity) -> Union[Company, None]:
        async with config.async_db as db:
            db.add(params)
            await db.commit()
            await db.refresh(params)
            return map_to_company(params)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def update(self, config: Config, params: CompanyUpdate) -> Union[Company, None]:
        async with config.async_db as db:
            stmt = select(CompanyEntity).filter(CompanyEntity.id == params.id)
            stmt.updated_date = datetime.now()
            result = await db.execute(stmt)
            company = result.scalars().first()

            if not company:
                return None

            update_data = params.model_dump(exclude_unset=True)
            for key, value in update_data.items():
                setattr(company, key, value)

            await db.commit()
            await db.refresh(company)
            return map_to_company(company)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def list(self, config: Config, params: Pagination) -> Union[List[Company], None]:
        async with config.async_db as db:
            stmt = select(CompanyEntity)

            if params.filters:
                stmt = get_filter(
                    query=stmt, filters=params.filters, entity=CompanyEntity
                )

            if not params.all_data:
                stmt = stmt.offset(params.skip).limit(params.limit)

            result = await db.execute(stmt)
            companys = result.scalars().all()

            if not companys:
                return None
            return map_to_list_company(companys)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def delete(
        self,
        config: Config,
        params: CompanyDelete,
    ) -> Union[Company, None]:
        async with config.async_db as db:
            stmt = select(CompanyEntity).filter(CompanyEntity.id == params.id)
            result = await db.execute(stmt)
            company = result.scalars().first()

            if not company:
                return None

            await db.delete(company)
            await db.commit()
            return map_to_company(company)

    @execute_transaction(layer=LAYER.I_D_R.value, enabled=settings.has_track)
    async def read(
        self,
        config: Config,
        params: CompanyRead,
    ) -> Union[Company, None]:
        async with config.async_db as db:
            stmt = select(CompanyEntity).filter(CompanyEntity.id == params.id)
            result = await db.execute(stmt)
            company = result.scalars().first()

            if not company:
                return None

            return map_to_company(company)
        