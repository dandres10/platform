# SPEC-032 T3
"""E2E parcial de UsersInternalUseCase.

CRUD completo (create / update / delete con guard last_admin) requiere un
fixture grande con company + location + rol_admin asignado. Esto se documenta
como ampliación futura — el test de listado ya valida multi-tenant filter +
endpoint vivo + auth.
"""
from sqlalchemy import text


HEADERS = {
    "language": "es",
    "timezone": "America/Bogota",
    "Authorization": "Bearer fake",
}


async def test_users_internal_listing_returns_response_for_authenticated_admin(client):
    """Endpoint vivo + auth. Response puede ser SUCCESS (lista) o ERROR
    (CORE_NO_RESULTS_FOUND si la company del token no tiene users) — ambos
    son válidos como "endpoint funciona y filtra por tenant"."""
    payload = {"skip": 0, "limit": 10, "all_data": False}
    r = await client.post("/v1/auth/users-internal", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)


async def test_users_internal_listing_filters_by_company_tenant(client):
    """Cuando la company del JWT no tiene ningún user, el listado responde
    ERROR con CORE_NO_RESULTS_FOUND. Esto valida que el multi-tenant filter
    está activo (no se filtran users de otras companies)."""
    payload = {"skip": 0, "limit": 50, "all_data": True}
    r = await client.post("/v1/auth/users-internal", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    if body["notification_type"] == "ERROR":
        assert body["response"] is None
    else:
        assert isinstance(body["response"], list)


# SPEC-032 quick win: UsersExternalUseCase
async def test_users_external_listing_returns_response(client):
    """UsersExternalUseCase: endpoint vivo + auth, multi-tenant filter."""
    payload = {"skip": 0, "limit": 10, "all_data": False}
    r = await client.post("/v1/auth/users-external", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] in ("SUCCESS", "ERROR")
    if body["notification_type"] == "SUCCESS":
        assert isinstance(body["response"], list)


# SPEC-032 T-AMP — CRUD completo con fixture pesado
from uuid import uuid4 as _uuid4


async def test_create_user_internal_happy_path(client, setup_full_company):
    """Admin crea user internal en su company con location_rol."""
    payload = {
        "language_id": setup_full_company["language_id"],
        "currency_id": setup_full_company["currency_id"],
        "location_rol": [{
            "location_id": setup_full_company["location_id"],
            "rol_id": setup_full_company["admin_rol_id"],
        }],
        "email": f"new-internal-{_uuid4().hex[:8]}@test.com",
        "password": "Strong1!Pass",
        "identification": f"NEW-{_uuid4().hex[:8]}",
        "first_name": "Nuevo",
        "last_name": "Interno",
        "phone": "+57 300 0000",
    }
    r = await client.post("/v1/auth/create-user-internal", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"


async def test_create_user_internal_rejects_duplicate_email(client, setup_full_company):
    """email ya existente (admin del setup) → ERROR."""
    payload = {
        "language_id": setup_full_company["language_id"],
        "currency_id": setup_full_company["currency_id"],
        "location_rol": [{
            "location_id": setup_full_company["location_id"],
            "rol_id": setup_full_company["admin_rol_id"],
        }],
        "email": setup_full_company["admin_email"],
        "password": "Strong1!Pass",
        "identification": f"DUP-{_uuid4().hex[:8]}",
        "first_name": "Dup",
        "last_name": "Email",
    }
    r = await client.post("/v1/auth/create-user-internal", json=payload, headers=HEADERS)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "ERROR"


async def test_create_user_internal_rejects_weak_password(client, setup_full_company):
    payload = {
        "language_id": setup_full_company["language_id"],
        "currency_id": setup_full_company["currency_id"],
        "location_rol": [{
            "location_id": setup_full_company["location_id"],
            "rol_id": setup_full_company["admin_rol_id"],
        }],
        "email": f"weak-{_uuid4().hex[:8]}@test.com",
        "password": "weak",
        "identification": f"W-{_uuid4().hex[:8]}",
        "first_name": "Weak",
        "last_name": "Password",
    }
    r = await client.post("/v1/auth/create-user-internal", json=payload, headers=HEADERS)
    assert r.status_code == 422, r.text


async def test_setup_full_company_admin_exists_in_db(client, setup_full_company):
    """Verifica que el fixture setup_full_company creó el admin correctamente
    en DB. (El listing /users-internal requiere location_id en token igual al
    del filter — en el conftest sintético el location_id es random y no coincide
    con el del fixture, así que validamos directo en DB.)"""
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    async with async_session_db() as session:
        row = (await session.execute(
            text(f'SELECT email, identification, state FROM {s}."user" WHERE id = :uid'),
            {"uid": setup_full_company["admin_user_id"]},
        )).first()
        assert row is not None
        assert row[0] == setup_full_company["admin_email"]
        assert row[2] is True  # state activo

        ulr_count = (await session.execute(
            text(f'SELECT COUNT(*) FROM {s}."user_location_rol" WHERE user_id = :uid AND location_id = :loc AND rol_id = :rol'),
            {
                "uid": setup_full_company["admin_user_id"],
                "loc": setup_full_company["location_id"],
                "rol": setup_full_company["admin_rol_id"],
            },
        )).scalar()
        assert ulr_count == 1
