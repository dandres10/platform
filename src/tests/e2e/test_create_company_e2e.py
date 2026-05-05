# SPEC-003 T9 / SPEC-001 R15 (atomicidad create_company)
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text


@pytest_asyncio.fixture(scope="function")
async def seed_ids(client):
    # SPEC-003 T9: currency fresca por test (UC SaveCompanyCurrency tiene bug
    # de validación global de duplicates — usar currency única por test).
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    fresh_currency_id = uuid4()
    async with async_session_db() as session:
        await session.execute(text(f"""
            INSERT INTO {s}."currency" (id, code, name, symbol, state)
            VALUES (:id, :code, 'Test Cur', '$', true)
        """), {"id": fresh_currency_id, "code": f"TC-{str(uuid4())[:6]}"})
        language = (await session.execute(text(f"SELECT id FROM {s}.\"language\" WHERE code='es' LIMIT 1"))).scalar()
        country = (await session.execute(text(f"SELECT id FROM {s}.\"geo_division\" WHERE level=0 LIMIT 1"))).scalar()
        admin_rol = (await session.execute(text(f"SELECT id FROM {s}.\"rol\" WHERE code='ADMIN' LIMIT 1"))).scalar()
        await session.commit()

    yield {
        "currency_id": str(fresh_currency_id),
        "language_id": str(language),
        "country_id": str(country),
        "admin_rol_id": str(admin_rol),
    }

    async with async_session_db() as session:
        # Borrar dependencias antes de la currency
        await session.execute(
            text(f'DELETE FROM {s}."currency_location" WHERE currency_id = :cid'),
            {"cid": fresh_currency_id},
        )
        await session.execute(
            text(f'DELETE FROM {s}."company_currency" WHERE currency_id = :cid'),
            {"cid": fresh_currency_id},
        )
        await session.execute(text(f'DELETE FROM {s}."currency" WHERE id = :cid'), {"cid": fresh_currency_id})
        await session.commit()


async def test_create_company_atomic(client, seed_ids):
    # SPEC-001 R15: create-company crea company + company_currency atómicamente
    nit = f"TEST-{str(uuid4())[:8]}"
    email = f"test-{str(uuid4())[:8]}@example.com"
    payload = {
        "company": {
            "name": "Test Company E2E",
            "nit": nit,
            "inactivity_time": 30,
            "company_base_currency_id": seed_ids["currency_id"],
        },
        "location": {
            "country_id": seed_ids["country_id"],
            "name": "Sede Principal Test",
            "address": "Calle 123 #45-67",
            "phone": "+57 3001234567",
            "email": f"loc-{email}",
        },
        "admin_user": {
            "email": email,
            "password": "Test1234!",
            "first_name": "Test",
            "last_name": "Admin",
            "identification": f"IDT-{str(uuid4())[:8]}",
            "phone": "+57 3001234567",
            "language_id": seed_ids["language_id"],
            "currency_id": seed_ids["currency_id"],
            "rol_id": seed_ids["admin_rol_id"],
        },
    }
    r = await client.post(
        "/v1/auth/create-company",
        json=payload,
        headers={"language": "es", "timezone": "America/Bogota"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["notification_type"] == "SUCCESS"

    # Verificar atomicidad: company + company_currency con is_base=true existen
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    async with async_session_db() as session:
        company_row = (await session.execute(
            text(f'SELECT id FROM {s}."company" WHERE nit = :nit'),
            {"nit": nit},
        )).first()
        assert company_row is not None
        company_id = company_row[0]

        cc_rows = (await session.execute(
            text(f'SELECT currency_id, is_base FROM {s}."company_currency" WHERE company_id = :cid'),
            {"cid": company_id},
        )).fetchall()
        assert len(cc_rows) == 1
        assert str(cc_rows[0][0]) == seed_ids["currency_id"]
        assert cc_rows[0][1] is True  # is_base=true

        # Cleanup: eliminar la company creada (cascada manual via _cleanup_test_data
        # del client fixture solo cubre COMPANY_ID y OTHER_COMPANY_ID; aquí necesitamos
        # cleanup explícito porque company_id es uno generado por el endpoint)
        await session.execute(text(f"""
            DELETE FROM {s}."user_location_rol" WHERE user_id IN (
                SELECT u.id FROM {s}."user" u
                JOIN {s}."platform" p ON p.id = u.platform_id
                JOIN {s}."location" l ON l.id = p.location_id
                WHERE l.company_id = :cid
            )
        """), {"cid": company_id})
        await session.execute(text(f"""
            DELETE FROM {s}."user" WHERE platform_id IN (
                SELECT p.id FROM {s}."platform" p
                JOIN {s}."location" l ON l.id = p.location_id
                WHERE l.company_id = :cid
            )
        """), {"cid": company_id})
        await session.execute(text(f"""
            DELETE FROM {s}."platform" WHERE location_id IN (
                SELECT id FROM {s}."location" WHERE company_id = :cid
            )
        """), {"cid": company_id})
        for tbl in ["menu_permission", "menu", "currency_location", "company_currency", "location"]:
            if tbl in ("menu_permission",):
                await session.execute(
                    text(f'DELETE FROM {s}."{tbl}" WHERE menu_id IN (SELECT id FROM {s}."menu" WHERE company_id = :cid)'),
                    {"cid": company_id},
                )
            elif tbl == "currency_location":
                await session.execute(
                    text(f'DELETE FROM {s}."{tbl}" WHERE location_id IN (SELECT id FROM {s}."location" WHERE company_id = :cid)'),
                    {"cid": company_id},
                )
            else:
                await session.execute(
                    text(f'DELETE FROM {s}."{tbl}" WHERE company_id = :cid'),
                    {"cid": company_id},
                )
        await session.execute(text(f'DELETE FROM {s}."company" WHERE id = :cid'), {"cid": company_id})
        await session.commit()


async def test_create_company_duplicate_nit_rejected(client, seed_ids):
    # SPEC-001: NIT duplicado retorna error
    nit = f"DUP-{str(uuid4())[:8]}"
    email1 = f"u1-{str(uuid4())[:8]}@x.com"
    email2 = f"u2-{str(uuid4())[:8]}@x.com"
    base_payload = {
        "company": {
            "name": "Test Company DUP",
            "nit": nit,
            "inactivity_time": 30,
            "company_base_currency_id": seed_ids["currency_id"],
        },
        "location": {
            "country_id": seed_ids["country_id"],
            "name": "Sede DUP",
            "address": "Calle 1",
            "phone": "+57 3001234567",
            "email": email1,
        },
        "admin_user": {
            "email": email1,
            "password": "Test1234!",
            "first_name": "Test",
            "last_name": "Admin",
            "identification": f"IDT-{str(uuid4())[:8]}",
            "phone": "+57 3001234567",
            "language_id": seed_ids["language_id"],
            "currency_id": seed_ids["currency_id"],
            "rol_id": seed_ids["admin_rol_id"],
        },
    }
    headers = {"language": "es", "timezone": "America/Bogota"}
    r1 = await client.post("/v1/auth/create-company", json=base_payload, headers=headers)
    assert r1.status_code == 200, r1.text

    base_payload["admin_user"]["email"] = email2
    base_payload["admin_user"]["identification"] = f"IDT-{str(uuid4())[:8]}"
    base_payload["location"]["email"] = email2
    r2 = await client.post("/v1/auth/create-company", json=base_payload, headers=headers)
    assert r2.status_code == 200, r2.text
    body2 = r2.json()
    assert body2["notification_type"] == "ERROR"
    assert "NIT" in body2["message"].upper()

    # Cleanup company creada
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema
    async with async_session_db() as session:
        company_row = (await session.execute(
            text(f'SELECT id FROM {s}."company" WHERE nit = :nit'),
            {"nit": nit},
        )).first()
        if company_row:
            cid = company_row[0]
            await session.execute(text(f"""
                DELETE FROM {s}."user_location_rol" WHERE user_id IN (
                    SELECT u.id FROM {s}."user" u
                    JOIN {s}."platform" p ON p.id = u.platform_id
                    JOIN {s}."location" l ON l.id = p.location_id
                    WHERE l.company_id = :cid
                )
            """), {"cid": cid})
            await session.execute(text(f"""
                DELETE FROM {s}."user" WHERE platform_id IN (
                    SELECT p.id FROM {s}."platform" p JOIN {s}."location" l ON l.id = p.location_id WHERE l.company_id = :cid
                )
            """), {"cid": cid})
            await session.execute(text(f"""
                DELETE FROM {s}."platform" WHERE location_id IN (SELECT id FROM {s}."location" WHERE company_id = :cid)
            """), {"cid": cid})
            await session.execute(
                text(f'DELETE FROM {s}."menu_permission" WHERE menu_id IN (SELECT id FROM {s}."menu" WHERE company_id = :cid)'),
                {"cid": cid},
            )
            await session.execute(
                text(f'DELETE FROM {s}."currency_location" WHERE location_id IN (SELECT id FROM {s}."location" WHERE company_id = :cid)'),
                {"cid": cid},
            )
            for tbl in ["menu", "company_currency", "location"]:
                await session.execute(text(f'DELETE FROM {s}."{tbl}" WHERE company_id = :cid'), {"cid": cid})
            await session.execute(text(f'DELETE FROM {s}."company" WHERE id = :cid'), {"cid": cid})
            await session.commit()
