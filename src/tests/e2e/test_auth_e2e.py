# SPEC-003 T10 / SPEC-002 Auth lifecycle
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text


@pytest_asyncio.fixture(scope="function")
async def seed_user(client):
    # Crea user externo de test para login + cleanup post-test
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    from src.core.classes.password import Password
    s = settings.database_schema

    user_id = uuid4()
    platform_id = uuid4()
    ulr_id = uuid4()
    email = f"e2e-{str(uuid4())[:8]}@test.com"
    password = "Test1234!"

    async with async_session_db() as session:
        language = (await session.execute(text(f"SELECT id FROM {s}.\"language\" LIMIT 1"))).scalar()
        currency = (await session.execute(text(f"SELECT id FROM {s}.\"currency\" LIMIT 1"))).scalar()
        rol_user = (await session.execute(text(f"SELECT id FROM {s}.\"rol\" WHERE code='USER' LIMIT 1"))).scalar()

        await session.execute(text(f"""
            INSERT INTO {s}."platform" (id, language_id, location_id, currency_id, token_expiration_minutes, refresh_token_expiration_minutes)
            VALUES (:pid, :lang, NULL, :curr, 60, 1440)
        """), {"pid": platform_id, "lang": language, "curr": currency})

        await session.execute(text(f"""
            INSERT INTO {s}."user" (id, platform_id, email, password, identification, first_name, last_name, phone, refresh_token, state)
            VALUES (:uid, :pid, :email, :pwd, :ident, 'E2E', 'Test', '+57 123', '', true)
        """), {
            "uid": user_id, "pid": platform_id, "email": email,
            "pwd": Password.hash_password(password=password),
            "ident": f"E2E-{str(uuid4())[:8]}",
        })

        await session.execute(text(f"""
            INSERT INTO {s}."user_location_rol" (id, user_id, location_id, rol_id, state)
            VALUES (:ulr, :uid, NULL, :rol, true)
        """), {"ulr": ulr_id, "uid": user_id, "rol": rol_user})
        await session.commit()

    yield {"email": email, "password": password, "user_id": str(user_id)}

    async with async_session_db() as session:
        await session.execute(text(f'DELETE FROM {s}."user_location_rol" WHERE user_id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."user" WHERE id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."platform" WHERE id = :pid'), {"pid": platform_id})
        await session.commit()


async def test_login_external_happy_path(client, seed_user):
    headers = {"language": "es", "timezone": "America/Bogota"}
    payload = {"email": seed_user["email"], "password": seed_user["password"]}
    r = await client.post("/v1/auth/login", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"
    assert body["response"]["token"]


async def test_login_invalid_credentials(client, seed_user):
    # SPEC-030 T8
    headers = {"language": "es", "timezone": "America/Bogota"}
    payload = {"email": seed_user["email"], "password": "WrongPassword"}
    r = await client.post("/v1/auth/login", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_login_nonexistent_user(client):
    # SPEC-030 T8
    headers = {"language": "es", "timezone": "America/Bogota"}
    payload = {"email": f"noexist-{uuid4()}@test.com", "password": "Test1234!"}
    r = await client.post("/v1/auth/login", json=payload, headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_logout_clears_refresh_token(client, seed_authenticated_external_user):
    headers = {"language": "es", "timezone": "America/Bogota", "Authorization": "Bearer fake"}
    r = await client.post("/v1/auth/logout", headers=headers)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"

    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema
    async with async_session_db() as session:
        row = (await session.execute(
            text(f'SELECT refresh_token FROM {s}."user" WHERE id = :uid'),
            {"uid": seed_authenticated_external_user["user_id"]},
        )).first()
        assert row is not None
        assert row[0] == ""


async def test_logout_idempotent_at_db_level(client, seed_authenticated_external_user):
    """Dos logouts seguidos: el primero limpia refresh_token, el segundo no falla aunque
    ya esté vacío. La validación de refresh_token vivo se hace en validate_has_refresh_token
    (cubierto por unit tests de Token); aquí validamos que el flow no rompe en re-llamadas."""
    headers = {"language": "es", "timezone": "America/Bogota", "Authorization": "Bearer fake"}
    r1 = await client.post("/v1/auth/logout", headers=headers)
    assert r1.status_code == 200

    r2 = await client.post("/v1/auth/logout", headers=headers)
    assert r2.status_code == 200, r2.text

    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema
    async with async_session_db() as session:
        row = (await session.execute(
            text(f'SELECT refresh_token FROM {s}."user" WHERE id = :uid'),
            {"uid": seed_authenticated_external_user["user_id"]},
        )).first()
        assert row[0] == ""
