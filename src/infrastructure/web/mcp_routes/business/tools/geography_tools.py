from src.infrastructure.web.mcp_routes.business.server import mcp
from src.core.classes.mcp_client import McpClient


@mcp.tool()
async def get_countries(language: str = "ES") -> str:
    """Listar todos los paises disponibles en la plataforma."""
    client = McpClient(language=language)
    return await client.get("/geography/countries")


@mcp.tool()
async def get_types_by_country(country_id: str, language: str = "ES") -> str:
    """Obtener tipos de division geografica de un pais (DEPARTMENT, CITY, COMMUNE, etc)."""
    client = McpClient(language=language)
    return await client.post("/geography/country/types", {"country_id": country_id})


@mcp.tool()
async def get_divisions_by_country_type(country_id: str, type_name: str, language: str = "ES") -> str:
    """Obtener todas las divisiones de un pais filtradas por tipo. Ej: todas las ciudades de Colombia."""
    client = McpClient(language=language)
    return await client.post("/geography/country/type", {"country_id": country_id, "type_name": type_name})


@mcp.tool()
async def get_children(parent_id: str, language: str = "ES") -> str:
    """Obtener hijos directos de una division geografica. Ej: ciudades de un departamento."""
    client = McpClient(language=language)
    return await client.post("/geography/children", {"parent_id": parent_id})


@mcp.tool()
async def get_children_by_type(parent_id: str, type_name: str, language: str = "ES") -> str:
    """Obtener descendientes recursivos por tipo. Busca en toda la jerarquia descendente."""
    client = McpClient(language=language)
    return await client.post("/geography/children/type", {"parent_id": parent_id, "type_name": type_name})


@mcp.tool()
async def get_hierarchy(node_id: str, language: str = "ES") -> str:
    """Obtener cadena de ancestros de una division. Ej: Colombia > Antioquia > Medellin."""
    client = McpClient(language=language)
    return await client.post("/geography/hierarchy", {"node_id": node_id})


@mcp.tool()
async def get_division_detail(node_id: str, language: str = "ES") -> str:
    """Obtener detalle completo de una division geografica por ID."""
    client = McpClient(language=language)
    return await client.post("/geography/detail", {"node_id": node_id})
