import re
from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient
from src.core.wrappers.check_mcp_roles import check_mcp_roles
from src.core.wrappers.check_mcp_permissions import check_mcp_permissions
from src.core.enums.rol_type import ROL_TYPE
from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.response import Response
from src.domain.models.business.catalog.list_companies.company_item import CompanyItem
from src.domain.models.business.catalog.list_locations_by_company.location_item import LocationItem

_UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.LIST.value])
async def list_companies(
    token: str,
    name_filter: str = "",
    skip: int = 0,
    limit: int = 20,
    language: str = "ES",
) -> Response[list[CompanyItem]]:
    """Buscar empresas por nombre. Retorna id, name, nit. Usar cuando el usuario no tiene empresa asignada o necesita company_id para consultar sedes y servicios.
Endpoint: POST platform /catalog/companies"""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "name", "condition": "like", "value": name_filter})
    raw = await client.post("/catalog/companies", {
        "skip": skip, "limit": limit, "filters": filters or None
    })
    return McpClient.parse_response(raw, Response[list[CompanyItem]])


@mcp.tool()
@check_mcp_roles([ROL_TYPE.ADMIN.value, ROL_TYPE.USER.value, ROL_TYPE.COLLA.value])
@check_mcp_permissions([PERMISSION_TYPE.LIST.value])
async def list_locations_by_company(
    token: str,
    company_id: str,
    name_filter: str = "",
    skip: int = 0,
    limit: int = 20,
    language: str = "ES",
) -> Response[list[LocationItem]]:
    """Sedes de una empresa. Retorna id, name, address, phone. Necesita company_id.
Endpoint: POST platform /catalog/locations"""
    if not _UUID_PATTERN.match(company_id):
        return Response.error(message=f'company_id invalido: "{company_id}". Debe ser un UUID valido del campo "id" del resultado de list_companies.')
    client = McpClient(token=token, language=language)
    filters = [{"field": "company_id", "condition": "==", "value": company_id}]
    if name_filter:
        filters.append({"field": "name", "condition": "like", "value": name_filter})
    raw = await client.post("/catalog/locations", {
        "skip": skip, "limit": limit, "filters": filters
    })
    return McpClient.parse_response(raw, Response[list[LocationItem]])
