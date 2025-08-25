from fastapi import FastAPI

# imports
from src.infrastructure.web.mcps_routes.mcp_router import mcp_router


class RouteMCPs:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(mcp_router)
