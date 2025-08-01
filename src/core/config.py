from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

env = os.getenv("ENV", "pc")
if env == "qa":
    load_dotenv(".env.qa")
elif env == "prod":
    load_dotenv(".env.prod")
elif env == "pc":
    load_dotenv(".env.pc")


print("*" * 100)
print(f"ENVIRONMENT: {os.getenv('APP_ENVIRONMENT')}")
print(f"PROJECT_NAME: {os.getenv('PROJECT_NAME')}")
print(f"PROJECT_VERSION: {os.getenv('PROJECT_VERSION')}")
print(f"HAS_TRACK: {os.getenv('HAS_TRACK')}")
print("*" * 100)


class Settings(BaseSettings):
    app_name: str = "Platform Management API"
    database_user: str = os.getenv("DATABASE_USER", "")
    database_password: str = os.getenv("DATABASE_PASSWORD", "")
    database_name: str = os.getenv("DATABASE_NAME", "")
    database_host: str = os.getenv("DATABASE_HOST", "")
    database_schema: str = os.getenv("DATABASE_SCHEMA", "")
    secret_key: str = os.getenv("SECRET_KEY", "")
    has_debug: bool = os.getenv("HAS_DEBUG", "False").lower() == "true"
    has_track: bool = os.getenv("HAS_TRACK", "False").lower() == "true"
    project_version: str = os.getenv("PROJECT_VERSION", "")
    project_name: str = os.getenv("PROJECT_NAME", "")
    project_description: str = os.getenv("PROJECT_DESCRIPTION", "")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "")
    app_environment: str = os.getenv("APP_ENVIRONMENT", "")

    class Config:
        env_file = ".env"


settings = Settings()
