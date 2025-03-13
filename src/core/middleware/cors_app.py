# middleware.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from src.core.config import settings


class CorsAppConfigurator:
    @staticmethod
    def setup_cors(app: FastAPI):
        if settings.app_environment == "production":
            allow_origins = ["https://example.com"]
        else:
            allow_origins = ["*"]

        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
