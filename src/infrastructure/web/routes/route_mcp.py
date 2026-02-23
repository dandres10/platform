from fastapi import APIRouter, status
from src.infrastructure.web.mcp_routes.business.server import mcp as mcp_business
import src.infrastructure.web.mcp_routes.business.tools.auth_tools      # noqa: F401
import src.infrastructure.web.mcp_routes.business.tools.geography_tools  # noqa: F401
import src.infrastructure.web.mcp_routes.business.tools.catalog_tools   # noqa: F401

mcp_info_router = APIRouter(
    prefix="/mcp",
    tags=["MCP"],
    responses={404: {"description": "Not found"}},
)


@mcp_info_router.get(
    "/info",
    status_code=status.HTTP_200_OK,
    summary="MCP Server info",
    description="Retorna informacion del MCP Server y lista de tools disponibles. "
    "Para conectarse como cliente MCP usar: `/mcp`",
)
async def mcp_business_info():
    tools = mcp_business._tool_manager._tools
    return {
        "name": mcp_business.name,
        "endpoint": "/mcp",
        "transport": "Streamable HTTP",
        "tools_count": len(tools),
        "tools": [
            {"name": name, "description": tool.description}
            for name, tool in sorted(tools.items())
        ],
    }


class RouteMcp:
    @staticmethod
    def set_routes(app):
        app.include_router(mcp_info_router)
        app.mount("/mcp", mcp_business.streamable_http_app())
