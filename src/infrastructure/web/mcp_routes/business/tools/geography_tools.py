from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient
from src.core.wrappers.check_mcp_roles import check_mcp_roles
from src.core.wrappers.check_mcp_permissions import check_mcp_permissions
from src.core.enums.rol_type import ROL_TYPE
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.response import Response
from src.domain.models.business.geography.geo_division_item_response import GeoDivisionItemResponse
from src.domain.models.business.geography.geo_division_type_by_country_response import GeoDivisionTypeByCountryResponse
from src.domain.models.business.geography.geo_division_hierarchy_response import GeoDivisionHierarchyResponse


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_countries(language: str = "ES") -> Response[list[GeoDivisionItemResponse]]:
    """Paises disponibles en la plataforma. Usar para seleccionar pais en formularios.
Endpoint: GET platform /geography/countries"""
    client = McpClient(language=language)
    raw = await client.get("/geography/countries")
    return McpClient.parse_response(raw, Response[list[GeoDivisionItemResponse]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_types_by_country(country_id: str, language: str = "ES") -> Response[list[GeoDivisionTypeByCountryResponse]]:
    """Tipos de division geografica de un pais (DEPARTMENT, CITY, etc). Necesita country_id.
Endpoint: POST platform /geography/country/types"""
    client = McpClient(language=language)
    raw = await client.post("/geography/country/types", {"country_id": country_id})
    return McpClient.parse_response(raw, Response[list[GeoDivisionTypeByCountryResponse]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_divisions_by_country_type(country_id: str, type_name: str, language: str = "ES") -> Response[list[GeoDivisionItemResponse]]:
    """Divisiones de un pais por tipo. Ej: todas las ciudades de Colombia. Necesita country_id y type_name.
Endpoint: POST platform /geography/country/type"""
    client = McpClient(language=language)
    raw = await client.post("/geography/country/type", {"country_id": country_id, "type_name": type_name})
    return McpClient.parse_response(raw, Response[list[GeoDivisionItemResponse]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_children(parent_id: str, language: str = "ES") -> Response[list[GeoDivisionItemResponse]]:
    """Hijos directos de una division. Ej: ciudades de Antioquia. Necesita parent_id.
Endpoint: POST platform /geography/children"""
    client = McpClient(language=language)
    raw = await client.post("/geography/children", {"parent_id": parent_id})
    return McpClient.parse_response(raw, Response[list[GeoDivisionItemResponse]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_children_by_type(parent_id: str, type_name: str, language: str = "ES") -> Response[list[GeoDivisionItemResponse]]:
    """Descendientes recursivos por tipo en toda la jerarquia. Necesita parent_id y type_name.
Endpoint: POST platform /geography/children/type"""
    client = McpClient(language=language)
    raw = await client.post("/geography/children/type", {"parent_id": parent_id, "type_name": type_name})
    return McpClient.parse_response(raw, Response[list[GeoDivisionItemResponse]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_hierarchy(node_id: str, language: str = "ES") -> Response[list[GeoDivisionHierarchyResponse]]:
    """Cadena de ancestros de una division. Ej: Colombia > Antioquia > Medellin. Necesita node_id.
Endpoint: POST platform /geography/hierarchy"""
    client = McpClient(language=language)
    raw = await client.post("/geography/hierarchy", {"node_id": node_id})
    return McpClient.parse_response(raw, Response[list[GeoDivisionHierarchyResponse]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.READ.value])
async def get_division_detail(node_id: str, language: str = "ES") -> Response[GeoDivisionItemResponse]:
    """Detalle de una division geografica. Necesita node_id.
Endpoint: POST platform /geography/detail"""
    client = McpClient(language=language)
    raw = await client.post("/geography/detail", {"node_id": node_id})
    return McpClient.parse_response(raw, Response[GeoDivisionItemResponse])
