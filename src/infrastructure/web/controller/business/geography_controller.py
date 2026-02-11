
from typing import List
from src.core.config import settings
from src.core.enums.layer import LAYER
from src.core.models.config import Config
from src.core.models.response import Response
from src.core.classes.async_message import Message
from src.core.models.message import MessageCoreEntity
from src.core.enums.keys_message import KEYS_MESSAGES
from src.core.wrappers.execute_transaction import execute_transaction
from src.domain.models.business.geography.index import (
    TypesByCountryRequest,
    ByCountryAndTypeRequest,
    ChildrenRequest,
    ChildrenByTypeRequest,
    HierarchyRequest,
    DetailRequest,
    GeoDivisionItemResponse,
    GeoDivisionTypeByCountryResponse,
    GeoDivisionHierarchyResponse,
)
from src.domain.services.use_cases.business.geography.countries.countries_use_case import (
    CountriesUseCase,
)
from src.domain.services.use_cases.business.geography.types_by_country.types_by_country_use_case import (
    TypesByCountryUseCase,
)
from src.domain.services.use_cases.business.geography.by_country_and_type.by_country_and_type_use_case import (
    ByCountryAndTypeUseCase,
)
from src.domain.services.use_cases.business.geography.children.children_use_case import (
    ChildrenUseCase,
)
from src.domain.services.use_cases.business.geography.children_by_type.children_by_type_use_case import (
    ChildrenByTypeUseCase,
)
from src.domain.services.use_cases.business.geography.hierarchy.hierarchy_use_case import (
    HierarchyUseCase,
)
from src.domain.services.use_cases.business.geography.detail.detail_use_case import (
    DetailUseCase,
)


class GeographyController:
    def __init__(self) -> None:
        self.message = Message()
        self.countries_use_case = CountriesUseCase()
        self.types_by_country_use_case = TypesByCountryUseCase()
        self.by_country_and_type_use_case = ByCountryAndTypeUseCase()
        self.children_use_case = ChildrenUseCase()
        self.children_by_type_use_case = ChildrenByTypeUseCase()
        self.hierarchy_use_case = HierarchyUseCase()
        self.detail_use_case = DetailUseCase()

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def countries(self, config: Config) -> Response[List[GeoDivisionItemResponse]]:
        result = await self.countries_use_case.execute(config=config)
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def types_by_country(self, config: Config, params: TypesByCountryRequest) -> Response[List[GeoDivisionTypeByCountryResponse]]:
        result = await self.types_by_country_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def by_country_and_type(
        self, config: Config, params: ByCountryAndTypeRequest
    ) -> Response[List[GeoDivisionItemResponse]]:
        result = await self.by_country_and_type_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def children(self, config: Config, params: ChildrenRequest) -> Response[List[GeoDivisionItemResponse]]:
        result = await self.children_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def children_by_type(
        self, config: Config, params: ChildrenByTypeRequest
    ) -> Response[List[GeoDivisionItemResponse]]:
        result = await self.children_by_type_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def hierarchy(self, config: Config, params: HierarchyRequest) -> Response[GeoDivisionHierarchyResponse]:
        result = await self.hierarchy_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )

    @execute_transaction(layer=LAYER.I_W_C_E.value, enabled=settings.has_track)
    async def detail(self, config: Config, params: DetailRequest) -> Response[GeoDivisionItemResponse]:
        result = await self.detail_use_case.execute(
            config=config, params=params
        )
        if isinstance(result, str):
            return Response.error(None, result)
        return Response.success_temporary_message(
            response=result,
            message=await self.message.get_message(
                config=config,
                message=MessageCoreEntity(key=KEYS_MESSAGES.CORE_QUERY_MADE.value),
            ),
        )
