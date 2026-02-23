from typing import List
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.models.filter import Pagination
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.catalog.list_companies import CompanyItem
from src.domain.models.business.catalog.list_locations_by_company import LocationItem
from src.domain.services.use_cases.business.catalog.list_companies.list_companies_use_case import (
    ListCompaniesUseCase,
)
from src.domain.services.use_cases.business.catalog.list_locations_by_company.list_locations_by_company_use_case import (
    ListLocationsByCompanyUseCase,
)


class CatalogController:
    def __init__(self) -> None:
        self.message = Message()
        self.list_companies_use_case = ListCompaniesUseCase()
        self.list_locations_by_company_use_case = ListLocationsByCompanyUseCase()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def list_companies(
        self, config: Config, params: Pagination
    ) -> Response[List[CompanyItem]]:
        result = await self.list_companies_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(response=None, message=result)

        return Response.success_temporary_message(
            response=[
                CompanyItem(
                    id=r.id,
                    name=r.name,
                    nit=r.nit,
                    state=r.state,
                )
                for r in result
            ],
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_QUERY_MADE.value
                ),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def list_locations_by_company(
        self, config: Config, params: Pagination
    ) -> Response[List[LocationItem]]:
        result = await self.list_locations_by_company_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(response=None, message=result)

        return Response.success_temporary_message(
            response=[
                LocationItem(
                    id=r.id,
                    company_id=r.company_id,
                    name=r.name,
                    address=r.address,
                    phone=r.phone,
                    email=r.email,
                    main_location=r.main_location,
                    country_id=r.country_id,
                    city_id=r.city_id,
                    latitude=r.latitude,
                    longitude=r.longitude,
                    state=r.state,
                )
                for r in result
            ],
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(
                    key=KEYS_MESSAGES.CORE_QUERY_MADE.value
                ),
            ),
        )
