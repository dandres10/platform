from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

string_db = f"postgresql+asyncpg://{settings.database_user}:{settings.database_password}@{settings.database_host}:5432/{settings.database_name}"

engine = create_async_engine(string_db, pool_size=20, echo=False)
async_db = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession  # Usando sesión asíncrona
)



@asynccontextmanager
async def async_session_db():
    async with async_db() as session:
        yield session



