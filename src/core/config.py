from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

env = os.getenv("ENV", "qa")
if env == "qa":
    load_dotenv(".env.qa")
elif env == "production":
    load_dotenv(".env.production")


print("*" * 100)
print(f"ENVIRONMENT: {os.getenv('APP_ENVIRONMENT')}")
print(f"PROJECT_NAME: {os.getenv('PROJECT_NAME')}")
print(f"PROJECT_VERSION: {os.getenv('PROJECT_VERSION')}")
print(f"HAS_TRACK: {os.getenv('HAS_TRACK')}")
print("*" * 100)


class Settings(BaseSettings):
    app_name: str = "Platform Management API"
    database_url: str = os.getenv("DATABASE_URL")
    secret_key: str = os.getenv("SECRET_KEY")
    has_debug: bool = os.getenv("HAS_DEBUG")
    has_track: bool = os.getenv("HAS_TRACK")
    project_version: str = os.getenv("PROJECT_VERSION")
    project_name: str = os.getenv("PROJECT_NAME")
    project_description: str = os.getenv("PROJECT_DESCRIPTION")
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM")

    class Config:
        env_file = ".env"


settings = Settings()
