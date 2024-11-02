from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

string_db = f"postgresql://{settings.database_user}:{settings.database_password}@{settings.database_host}:5432/{settings.database_name}"

session_db = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=create_engine(string_db, pool_size=20)
)



