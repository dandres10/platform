# SPEC-032 T4
"""E2E para los 4 UCs de auth completeness (SPEC-006).

Cubre create-user-external (post T11.a con welcome + JWT), change-password
(T12), forgot-password (T13) y reset-password (T14).
"""
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest_asyncio
from sqlalchemy import text


HEADERS = {"language": "es", "timezone": "America/Bogota"}
HEADERS_AUTH = {**HEADERS, "Authorization": "Bearer fake"}


# ---------------------------------------------------------------------------
# create-user-external (SPEC-006 T11.a) — público
# ---------------------------------------------------------------------------


async def test_create_user_external_returns_jwt_and_user_id(client):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    async with async_session_db() as session:
        language_id = (await session.execute(
            text(f"SELECT id FROM {s}.\"language\" WHERE code='es' LIMIT 1")
        )).scalar()
        currency_id = (await session.execute(
            text(f"SELECT id FROM {s}.\"currency\" LIMIT 1")
        )).scalar()

    payload = {
        "language_id": str(language_id),
        "currency_id": str(currency_id),
        "email": f"e2e-create-ext-{uuid4().hex[:8]}@test.com",
        "password": "Strong1!Pass",
        "identification": f"E2E-CRE-{uuid4().hex[:8]}",
        "first_name": "Create",
        "last_name": "External",
        "phone": "+57 300 1234567",
    }
    r = await client.post("/v1/auth/create-user-external", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"
    assert body["response"]["user_id"]
    assert body["response"]["token"]
    assert body["response"]["refresh_token"]

    # cleanup
    user_id = body["response"]["user_id"]
    async with async_session_db() as session:
        await session.execute(text(f'DELETE FROM {s}."user_location_rol" WHERE user_id = :uid'), {"uid": user_id})
        platform_row = (await session.execute(
            text(f'SELECT platform_id FROM {s}."user" WHERE id = :uid'), {"uid": user_id}
        )).first()
        await session.execute(text(f'DELETE FROM {s}."user" WHERE id = :uid'), {"uid": user_id})
        if platform_row:
            await session.execute(text(f'DELETE FROM {s}."platform" WHERE id = :pid'), {"pid": platform_row[0]})
        await session.commit()


async def test_create_user_external_rejects_weak_password(client):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    async with async_session_db() as session:
        language_id = (await session.execute(
            text(f"SELECT id FROM {s}.\"language\" WHERE code='es' LIMIT 1")
        )).scalar()
        currency_id = (await session.execute(
            text(f"SELECT id FROM {s}.\"currency\" LIMIT 1")
        )).scalar()

    payload = {
        "language_id": str(language_id),
        "currency_id": str(currency_id),
        "email": f"e2e-weak-{uuid4().hex[:8]}@test.com",
        "password": "weakpass",
        "identification": f"E2E-W-{uuid4().hex[:8]}",
        "first_name": "Weak",
        "last_name": "Pass",
    }
    r = await client.post("/v1/auth/create-user-external", json=payload, headers=HEADERS)
    assert r.status_code == 422, r.text


# ---------------------------------------------------------------------------
# forgot-password (SPEC-006 T13) — público
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture(scope="function")
async def seed_external_user_for_password_flows(client):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    from src.core.classes.password import Password
    s = settings.database_schema

    user_id = uuid4()
    platform_id = uuid4()
    ulr_id = uuid4()
    email = f"e2e-pwd-{uuid4().hex[:8]}@test.com"
    password = "InitialP1!"

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
            VALUES (:uid, :pid, :email, :pwd, :ident, 'PWD', 'Test', '+57 300', 'rt', true)
        """), {
            "uid": user_id, "pid": platform_id, "email": email,
            "pwd": Password.hash_password(password=password),
            "ident": f"PWD-{uuid4().hex[:8]}",
        })
        await session.execute(text(f"""
            INSERT INTO {s}."user_location_rol" (id, user_id, location_id, rol_id, state)
            VALUES (:ulr, :uid, NULL, :rol, true)
        """), {"ulr": ulr_id, "uid": user_id, "rol": rol_user})
        await session.commit()

    yield {"user_id": str(user_id), "email": email, "password": password}

    async with async_session_db() as session:
        await session.execute(text(f'DELETE FROM {s}."password_reset_token" WHERE user_id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."user_location_rol" WHERE user_id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."user" WHERE id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."platform" WHERE id = :pid'), {"pid": platform_id})
        await session.commit()


async def test_forgot_password_creates_reset_token_for_existing_email(client, seed_external_user_for_password_flows):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    payload = {"email": seed_external_user_for_password_flows["email"]}
    r = await client.post("/v1/auth/forgot-password", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"

    async with async_session_db() as session:
        rows = (await session.execute(
            text(f'SELECT token, used_at FROM {s}."password_reset_token" WHERE user_id = :uid'),
            {"uid": seed_external_user_for_password_flows["user_id"]},
        )).fetchall()
        assert len(rows) == 1
        token_value, used_at = rows[0]
        assert token_value
        assert used_at is None


async def test_forgot_password_silent_for_nonexistent_email_no_leak(client):
    payload = {"email": f"ghost-{uuid4().hex[:8]}@noexist.com"}
    r = await client.post("/v1/auth/forgot-password", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"


# ---------------------------------------------------------------------------
# reset-password (SPEC-006 T14) — público
# ---------------------------------------------------------------------------


async def test_reset_password_consumes_token_and_changes_password(client, seed_external_user_for_password_flows):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    from src.core.classes.password import Password
    s = settings.database_schema

    token_value = uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    async with async_session_db() as session:
        await session.execute(text(f"""
            INSERT INTO {s}."password_reset_token" (id, user_id, token, expires_at, used_at, state)
            VALUES (:id, :uid, :tk, :exp, NULL, true)
        """), {
            "id": uuid4(),
            "uid": seed_external_user_for_password_flows["user_id"],
            "tk": token_value,
            "exp": expires_at,
        })
        await session.commit()

    payload = {"token": token_value, "new_password": "PostReset1!"}
    r = await client.post("/v1/auth/reset-password", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"

    async with async_session_db() as session:
        token_row = (await session.execute(
            text(f'SELECT used_at FROM {s}."password_reset_token" WHERE token = :tk'),
            {"tk": token_value},
        )).first()
        assert token_row is not None
        assert token_row[0] is not None  # used_at != NULL

        user_row = (await session.execute(
            text(f'SELECT password FROM {s}."user" WHERE id = :uid'),
            {"uid": seed_external_user_for_password_flows["user_id"]},
        )).first()
        assert Password.check_password(password="PostReset1!", hashed_password=user_row[0])


async def test_reset_password_rejects_invalid_token(client):
    payload = {"token": "00000000000000000000000000000000", "new_password": "Strong1!Pass"}
    r = await client.post("/v1/auth/reset-password", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_reset_password_rejects_already_used_token(client, seed_external_user_for_password_flows):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    token_value = uuid4().hex
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    used_at = datetime.now(timezone.utc)
    async with async_session_db() as session:
        await session.execute(text(f"""
            INSERT INTO {s}."password_reset_token" (id, user_id, token, expires_at, used_at, state)
            VALUES (:id, :uid, :tk, :exp, :used, true)
        """), {
            "id": uuid4(),
            "uid": seed_external_user_for_password_flows["user_id"],
            "tk": token_value,
            "exp": expires_at,
            "used": used_at,
        })
        await session.commit()

    payload = {"token": token_value, "new_password": "Strong1!Pass"}
    r = await client.post("/v1/auth/reset-password", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_reset_password_rejects_weak_new_password(client):
    payload = {"token": "doesntmatter12345", "new_password": "weak"}
    r = await client.post("/v1/auth/reset-password", json=payload, headers=HEADERS)
    assert r.status_code == 422, r.text


# ---------------------------------------------------------------------------
# change-password (SPEC-006 T12) — autenticado
# ---------------------------------------------------------------------------


async def test_change_password_with_correct_old_succeeds(client, seed_authenticated_external_user):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    from src.core.classes.password import Password
    s = settings.database_schema

    # El seed_authenticated_external_user usa Password "Test1234!" para hashear
    # (ver fixture en test_auth_e2e). Pero NOSOTROS no necesitamos verificar
    # contra la password real — el endpoint busca el hash en DB.
    # Para que el test sea robusto, primero seteamos un hash conocido.
    async with async_session_db() as session:
        await session.execute(
            text(f'UPDATE {s}."user" SET password = :pwd WHERE id = :uid'),
            {"pwd": Password.hash_password(password="OldStrong1!"), "uid": seed_authenticated_external_user["user_id"]},
        )
        await session.commit()

    payload = {"old_password": "OldStrong1!", "new_password": "NewStrong2!"}
    r = await client.post("/v1/auth/change-password", json=payload, headers=HEADERS_AUTH)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"

    async with async_session_db() as session:
        row = (await session.execute(
            text(f'SELECT password, password_changed_at FROM {s}."user" WHERE id = :uid'),
            {"uid": seed_authenticated_external_user["user_id"]},
        )).first()
        assert Password.check_password(password="NewStrong2!", hashed_password=row[0])
        assert row[1] is not None  # password_changed_at se setea


async def test_change_password_with_incorrect_old_returns_error(client, seed_authenticated_external_user):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    from src.core.classes.password import Password
    s = settings.database_schema

    async with async_session_db() as session:
        await session.execute(
            text(f'UPDATE {s}."user" SET password = :pwd WHERE id = :uid'),
            {"pwd": Password.hash_password(password="CorrectOld1!"), "uid": seed_authenticated_external_user["user_id"]},
        )
        await session.commit()

    payload = {"old_password": "WrongOld1!", "new_password": "NewStrong2!"}
    r = await client.post("/v1/auth/change-password", json=payload, headers=HEADERS_AUTH)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_change_password_rejects_weak_new_password(client):
    payload = {"old_password": "anything", "new_password": "weak"}
    r = await client.post("/v1/auth/change-password", json=payload, headers=HEADERS_AUTH)
    assert r.status_code == 422, r.text


# SPEC-032 quick win — gaps en UCs ya cubiertos
# ---------------------------------------------------------------------------


async def test_create_user_external_rejects_duplicate_email(client, seed_external_user_for_password_flows):
    """CreateUserExternalUseCase guard: email duplicado debería rechazar."""
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    async with async_session_db() as session:
        language_id = (await session.execute(text(f"SELECT id FROM {s}.\"language\" WHERE code='es' LIMIT 1"))).scalar()
        currency_id = (await session.execute(text(f"SELECT id FROM {s}.\"currency\" LIMIT 1"))).scalar()

    payload = {
        "language_id": str(language_id),
        "currency_id": str(currency_id),
        "email": seed_external_user_for_password_flows["email"],
        "password": "Strong1!Pass",
        "identification": f"DUP-EMAIL-{uuid4().hex[:8]}",
        "first_name": "Dup",
        "last_name": "Email",
    }
    r = await client.post("/v1/auth/create-user-external", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_reset_password_rejects_expired_token(client, seed_external_user_for_password_flows):
    """Token con expires_at en el pasado → AUTH_RESET_PASSWORD_TOKEN_EXPIRED."""
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    token_value = uuid4().hex
    expired_at = datetime.now(timezone.utc) - timedelta(hours=2)
    async with async_session_db() as session:
        await session.execute(text(f"""
            INSERT INTO {s}."password_reset_token" (id, user_id, token, expires_at, used_at, state)
            VALUES (:id, :uid, :tk, :exp, NULL, true)
        """), {
            "id": uuid4(),
            "uid": seed_external_user_for_password_flows["user_id"],
            "tk": token_value,
            "exp": expired_at,
        })
        await session.commit()

    payload = {"token": token_value, "new_password": "Strong1!Pass"}
    r = await client.post("/v1/auth/reset-password", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_forgot_password_token_has_one_hour_ttl(client, seed_external_user_for_password_flows):
    """Verifica que expires_at se setea ~now+60min (RESET_TOKEN_TTL_MINUTES=60).

    Compara contra el clock de Python (no contra created_date de PostgreSQL)
    porque pueden estar en zonas horarias distintas en infraestructuras
    no-UTC."""
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    payload = {"email": seed_external_user_for_password_flows["email"]}
    before_post = datetime.now(timezone.utc)
    r = await client.post("/v1/auth/forgot-password", json=payload, headers=HEADERS)
    after_post = datetime.now(timezone.utc)
    assert r.status_code == 200, r.text

    async with async_session_db() as session:
        row = (await session.execute(
            text(f'SELECT expires_at FROM {s}."password_reset_token" WHERE user_id = :uid ORDER BY created_date DESC LIMIT 1'),
            {"uid": seed_external_user_for_password_flows["user_id"]},
        )).first()
        assert row is not None
        expires_at = row[0]

        expected_min = before_post + timedelta(minutes=60)
        expected_max = after_post + timedelta(minutes=60)
        # Tolerancia ±2s por overhead del request
        assert (expected_min - timedelta(seconds=2)) <= expires_at <= (expected_max + timedelta(seconds=2)), (
            f"Expected expires_at ~now+60min ({expected_min}–{expected_max}), got {expires_at}"
        )
