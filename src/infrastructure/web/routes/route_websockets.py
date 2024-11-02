from fastapi import FastAPI

# imports
from src.infrastructure.web.websockets_routes.example_router import example_router




class RouteWebsockets:
    @staticmethod
    def set_routes(app: FastAPI):
        # include_router
        app.include_router(example_router)
