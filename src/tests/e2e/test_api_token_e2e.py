# SPEC-032 T2
import pytest_asyncio
from uuid import uuid4

from sqlalchemy import text


@pytest_asyncio.fixture(scope="function")
async def rol_for_api_token(client):
    """Toma un rol global existente (CHECK constraint solo permite ADMIN/COLLA/USER)
    y limpia api_tokens previos para que el test arranque limpio."""
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    async with async_session_db() as session:
        rol_row = (await session.execute(
            text(f"SELECT id, code FROM {s}.\"rol\" WHERE code = 'COLLA' AND company_id IS NULL LIMIT 1")
        )).first()
        assert rol_row is not None, "Seed data: rol COLLA global no encontrado en DB"
        rol_id, rol_code = rol_row[0], rol_row[1]

        await session.execute(
            text(f'DELETE FROM {s}."api_token" WHERE rol_id = :rid'),
            {"rid": rol_id},
        )
        await session.commit()

    yield {"rol_id": str(rol_id), "code": rol_code}

    async with async_session_db() as session:
        await session.execute(
            text(f'DELETE FROM {s}."api_token" WHERE rol_id = :rid'),
            {"rid": rol_id},
        )
        await session.commit()


HEADERS = {
    "language": "es",
    "timezone": "America/Bogota",
    "Authorization": "Bearer fake",
}


async def test_create_api_token_happy_path(client, rol_for_api_token):
    payload = {"rol_id": rol_for_api_token["rol_id"]}
    r = await client.post("/v1/auth/create-api-token", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"
    assert body["response"]["rol_id"] == rol_for_api_token["rol_id"]
    assert body["response"]["rol_code"] == rol_for_api_token["code"]


async def test_create_api_token_with_nonexistent_rol_returns_error(client):
    fake_rol_id = str(uuid4())
    payload = {"rol_id": fake_rol_id}
    r = await client.post("/v1/auth/create-api-token", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_create_api_token_duplicate_rejected(client, rol_for_api_token):
    payload = {"rol_id": rol_for_api_token["rol_id"]}

    r1 = await client.post("/v1/auth/create-api-token", json=payload, headers=HEADERS)
    assert r1.status_code == 200
    assert r1.json()["notification_type"] == "SUCCESS"

    r2 = await client.post("/v1/auth/create-api-token", json=payload, headers=HEADERS)
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["notification_type"] == "ERROR"
