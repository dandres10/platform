from typing import AsyncGenerator
from src.core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession


string_db = (
    f"postgresql+asyncpg://{settings.database_user}:"
    f"{settings.database_password}@{settings.database_host}:5432/"
    f"{settings.database_name}"
)

# SPEC-012: pool conservador para `db.t4g.micro` (1 GB RAM, ~100 conexiones
# efectivas) compartida entre los 4 backends del ecosistema. Con UoW por request,
# cada conexión queda tomada toda la duración del request, así que el pool debe
# quedar bajo el límite total: 4 backends × 25 max = 100. Alineado con inventory
# (SPEC-099 T9). Si métricas en prod muestran saturación, revisar.
engine = create_async_engine(
    string_db,
    pool_size=15,
    max_overflow=10,
    pool_timeout=10,
    pool_recycle=3600,
    echo=False,
)

async_db = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=engine,
    class_=AsyncSession,
)


@asynccontextmanager
async def async_session_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_db() as session:
        yield session
