from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from src.infrastructure.database.config.async_config_db import async_session_db

health_router = APIRouter(tags=["Health"])


# SPEC-021
@health_router.get("/health")
async def health():
    db_ok = False
    try:
        async with async_session_db() as session:
            await session.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if db_ok else "degraded",
        "service": "platform",
        "database": "connected" if db_ok else "disconnected",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
