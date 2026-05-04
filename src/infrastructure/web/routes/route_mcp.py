from fastapi import APIRouter, Header, status
from typing import Optional
from src.infrastructure.web.mcp_routes.business.server import mcp as mcp_business
from src.core.classes.token import Token
import src.infrastructure.web.mcp_routes.business.tools.auth_tools      # noqa: F401
import src.infrastructure.web.mcp_routes.business.tools.geography_tools  # noqa: F401
import src.infrastructure.web.mcp_routes.business.tools.catalog_tools   # noqa: F401

mcp_info_router = APIRouter(
    prefix="/v1/mcp",
    tags=["MCP"],
    responses={404: {"description": "Not found"}},
)


def _tool_to_dict(name: str, tool) -> dict:
    d = {"name": name, "description": tool.description, "parameters": tool.parameters}
    if hasattr(tool, 'output_schema') and tool.output_schema:
        d["output_schema"] = tool.output_schema
    return d


def _filter_tools(tools: dict, rol_code: str, permissions: list[str]) -> list[dict]:
    result = []
    for name, tool in sorted(tools.items()):
        fn = tool.fn
        allowed_roles = getattr(fn, "_mcp_roles", None)
        required_perms = getattr(fn, "_mcp_permissions", None)
        if allowed_roles is not None and rol_code not in allowed_roles:
            continue
        if required_perms is not None and not any(p in permissions for p in required_perms):
            continue
        result.append(_tool_to_dict(name, tool))
    return result


@mcp_info_router.get(
    "/info",
    status_code=status.HTTP_200_OK,
    summary="MCP Server info",
    description="Retorna informacion del MCP Server y lista de tools disponibles. "
    "Con Authorization header filtra por rol y permisos del token. "
    "Para conectarse como cliente MCP usar: `/v1/mcp`",
)
async def mcp_business_info(authorization: Optional[str] = Header(None)):
    tools = mcp_business._tool_manager._tools
    if authorization and authorization.startswith("Bearer "):
        raw_token = authorization.replace("Bearer ", "")
        access_token = Token().verify_token(raw_token)
        filtered = _filter_tools(tools, access_token.rol_code, access_token.permissions)
        return {
            "name": mcp_business.name,
            "endpoint": "/v1/mcp",
            "transport": "Streamable HTTP",
            "tools_count": len(filtered),
            "tools": filtered,
        }
    return {
        "name": mcp_business.name,
        "endpoint": "/v1/mcp",
        "transport": "Streamable HTTP",
        "tools_count": len(tools),
        "tools": [
            _tool_to_dict(name, tool)
            for name, tool in sorted(tools.items())
        ],
    }


class RouteMcp:
    @staticmethod
    def set_routes(app):
        app.include_router(mcp_info_router)
        app.mount("/v1/mcp", mcp_business.streamable_http_app())
