import re
from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient

_UUID_PATTERN = re.compile(
    r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
)


@mcp.tool()
async def list_companies(
    token: str,
    name_filter: str = "",
    skip: int = 0,
    limit: int = 20,
    language: str = "ES",
) -> str:
    """Listar empresas/companias registradas en la plataforma con paginacion y filtro opcional por nombre.
    Usa esta tool para buscar una empresa por nombre cuando el usuario quiere agendar una cita
    y necesitas conocer el company_id (campo "id" en cada item del resultado)."""
    client = McpClient(token=token, language=language)
    filters = []
    if name_filter:
        filters.append({"field": "name", "condition": "like", "value": name_filter})
    return await client.post("/catalog/companies", {
        "skip": skip, "limit": limit, "filters": filters or None
    })


@mcp.tool()
async def list_locations_by_company(
    token: str,
    company_id: str,
    name_filter: str = "",
    skip: int = 0,
    limit: int = 20,
    language: str = "ES",
) -> str:
    """Listar sucursales/ubicaciones de una empresa especifica.
    company_id: UUID obtenido del campo "id" del resultado de list_companies.
    Retorna ubicaciones con su location_id (campo "id"), necesario para consultar servicios y disponibilidad."""
    if not _UUID_PATTERN.match(company_id):
        return f'{{"error": "company_id invalido: \\"{company_id}\\\". Debe ser un UUID valido del campo \\"id\\" del resultado de list_companies."}}'
    client = McpClient(token=token, language=language)
    filters = [{"field": "company_id", "condition": "==", "value": company_id}]
    if name_filter:
        filters.append({"field": "name", "condition": "like", "value": name_filter})
    return await client.post("/catalog/locations", {
        "skip": skip, "limit": limit, "filters": filters
    })
