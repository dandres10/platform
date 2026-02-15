
from typing import List
from src.core.config import settings
from src.core.models.config import Config
from src.core.models.response import Response
from fastapi import APIRouter, Depends, status
from src.core.methods.get_config import get_config_public
from src.core.wrappers.execute_transaction import execute_transaction_route
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
from src.infrastructure.web.controller.business.geography_controller import (
    GeographyController,
)


geography_router = APIRouter(
    prefix="/geography",
    tags=["Geography"],
    responses={404: {"description": "Not found"}},
)

geography_controller = GeographyController()


# ============================================
# GET /geography/countries
# Listar todos los países disponibles en el sistema
# ============================================
@geography_router.get(
    "/countries",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionItemResponse]],
    summary="Listar países",
    description="""
    Retorna todos los países disponibles (nodos raíz de nivel 0).
    Usado para poblar selectores y navegar la jerarquía geográfica.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def countries(config: Config = Depends(get_config_public)) -> Response[List[GeoDivisionItemResponse]]:
    return await geography_controller.countries(config=config)


# ============================================
# POST /geography/country/types
# Obtener tipos de división geográfica disponibles para un país
# ============================================
@geography_router.post(
    "/country/types",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionTypeByCountryResponse]],
    summary="Tipos de división por país",
    description="""
    Obtiene los tipos de división disponibles para un país (DEPARTMENT, CITY, COMMUNE, etc.) 
    con conteo de registros por tipo. Útil para mostrar estructura geográfica y estadísticas.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def types_by_country(
    params: TypesByCountryRequest, config: Config = Depends(get_config_public)
) -> Response[List[GeoDivisionTypeByCountryResponse]]:
    return await geography_controller.types_by_country(
        config=config, params=params
    )


# ============================================
# POST /geography/country/type
# Obtener todas las divisiones de un país filtradas por tipo
# ============================================
@geography_router.post(
    "/country/type",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionItemResponse]],
    summary="Divisiones por país y tipo",
    description="""
    Obtiene todas las divisiones de un país filtradas por tipo específico (búsqueda recursiva).
    Ejemplo: listar todos los departamentos de Colombia o todas las ciudades de un país.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def by_country_and_type(
    params: ByCountryAndTypeRequest, config: Config = Depends(get_config_public)
) -> Response[List[GeoDivisionItemResponse]]:
    return await geography_controller.by_country_and_type(
        config=config, params=params
    )


# ============================================
# POST /geography/children
# Obtener hijos directos de una división geográfica
# ============================================
@geography_router.post(
    "/children",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionItemResponse]],
    summary="Hijos directos de división",
    description="""
    Obtiene hijos directos (un nivel) de una división geográfica.
    Ejemplo: ciudades de un departamento, comunas de una ciudad.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def children(params: ChildrenRequest, config: Config = Depends(get_config_public)) -> Response[List[GeoDivisionItemResponse]]:
    return await geography_controller.children(
        config=config, params=params
    )


# ============================================
# POST /geography/children/type
# Obtener descendientes de una división filtrados por tipo
# ============================================
@geography_router.post(
    "/children/type",
    status_code=status.HTTP_200_OK,
    response_model=Response[List[GeoDivisionItemResponse]],
    summary="Descendientes por tipo",
    description="""
    Obtiene descendientes (búsqueda recursiva) de una división filtrados por tipo.
    A diferencia de `/children`, busca en toda la jerarquía descendente.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def children_by_type(
    params: ChildrenByTypeRequest, config: Config = Depends(get_config_public)
) -> Response[List[GeoDivisionItemResponse]]:
    return await geography_controller.children_by_type(
        config=config, params=params
    )


# ============================================
# POST /geography/hierarchy
# Obtener jerarquía completa hacia arriba (ancestros)
# ============================================
@geography_router.post(
    "/hierarchy",
    status_code=status.HTTP_200_OK,
    response_model=Response[GeoDivisionHierarchyResponse],
    summary="Jerarquía de ancestros",
    description="""
    Obtiene la jerarquía completa desde el nodo hasta el país (ancestros).
    Útil para breadcrumbs: Colombia > Antioquia > Medellín > Comuna 10.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def hierarchy(params: HierarchyRequest, config: Config = Depends(get_config_public)) -> Response[GeoDivisionHierarchyResponse]:
    return await geography_controller.hierarchy(
        config=config, params=params
    )


# ============================================
# POST /geography/detail
# Obtener detalle completo de una división geográfica
# ============================================
@geography_router.post(
    "/detail",
    status_code=status.HTTP_200_OK,
    response_model=Response[GeoDivisionItemResponse],
    summary="Detalle de división",
    description="""
    Obtiene información completa de una división geográfica por ID.
    Incluye nombre, código, nivel, tipo y estado.
    """,
)
@execute_transaction_route(enabled=settings.has_track)
async def detail(params: DetailRequest, config: Config = Depends(get_config_public)) -> Response[GeoDivisionItemResponse]:
    return await geography_controller.detail(
        config=config, params=params
    )
