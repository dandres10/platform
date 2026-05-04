# SPEC-003 T9 / SPEC-001
import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy import text

from src.tests.e2e import _tenant_state


@pytest_asyncio.fixture(scope="function")
async def setup_company(client):
    # SPEC-003 T9: cada test tiene su propio company_id (UUID nuevo) para
    # aislamiento. Inserta company + 2 currencies de test.
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    s = settings.database_schema

    company_id = uuid4()
    nit = f"TEST-{str(uuid4())[:8]}"
    currency_a_id = uuid4()
    currency_b_id = uuid4()

    async with async_session_db() as session:
        await session.execute(text(f"""
            INSERT INTO {s}."company" (id, nit, name, state)
            VALUES (:cid, :nit, 'Test Company', true)
        """), {"cid": company_id, "nit": nit})
        for cid, code in [(currency_a_id, f'TA-{str(uuid4())[:6]}'), (currency_b_id, f'TB-{str(uuid4())[:6]}')]:
            await session.execute(text(f"""
                INSERT INTO {s}."currency" (id, code, name, symbol, state)
                VALUES (:id, :code, 'Test Currency', '$', true)
            """), {"id": cid, "code": code})
        await session.commit()

    # Switch tenant para que el token use este company_id
    with _tenant_state.switch_tenant(str(company_id)):
        yield {"company_id": str(company_id), "currency_a": str(currency_a_id), "currency_b": str(currency_b_id)}

    # Cleanup: borrar company_currency, currencies y company
    async with async_session_db() as session:
        await session.execute(
            text(f'DELETE FROM {s}."company_currency" WHERE company_id = :cid'),
            {"cid": company_id},
        )
        await session.execute(
            text(f'DELETE FROM {s}."currency" WHERE id IN (:a, :b)'),
            {"a": currency_a_id, "b": currency_b_id},
        )
        await session.execute(
            text(f'DELETE FROM {s}."company" WHERE id = :cid'),
            {"cid": company_id},
        )
        await session.commit()


async def test_save_first_company_currency_must_be_base(client, setup_company):
    # SPEC-001 PLT-005: primera currency debe ser base
    payload = {
        "company_id": setup_company["company_id"],
        "currency_id": setup_company["currency_a"],
        "is_base": False,
    }
    r = await client.post("/company-currency", json=payload, headers={"language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 409
    assert "PLT-005" in r.text


async def test_save_company_currency_happy_path(client, setup_company):
    payload = {
        "company_id": setup_company["company_id"],
        "currency_id": setup_company["currency_a"],
        "is_base": True,
    }
    r = await client.post("/company-currency", json=payload, headers={"language": "es", "timezone": "America/Bogota"})
    assert r.status_code == 200
    body = r.json()
    assert body["notification_type"] == "SUCCESS"


async def test_save_duplicate_currency_rejected(client, setup_company):
    # SPEC-001 PLT-001: misma currency duplicada
    headers = {"language": "es", "timezone": "America/Bogota"}
    payload = {
        "company_id": setup_company["company_id"],
        "currency_id": setup_company["currency_a"],
        "is_base": True,
    }
    r1 = await client.post("/company-currency", json=payload, headers=headers)
    assert r1.status_code == 200
    r2 = await client.post("/company-currency", json=payload, headers=headers)
    assert r2.status_code == 409
    assert "PLT-001" in r2.text


async def test_save_second_base_rejected(client, setup_company):
    # SPEC-001 PLT-002: segunda currency con is_base=true rechazada
    headers = {"language": "es", "timezone": "America/Bogota"}
    p1 = {"company_id": setup_company["company_id"], "currency_id": setup_company["currency_a"], "is_base": True}
    r1 = await client.post("/company-currency", json=p1, headers=headers)
    assert r1.status_code == 200

    p2 = {"company_id": setup_company["company_id"], "currency_id": setup_company["currency_b"], "is_base": True}
    r2 = await client.post("/company-currency", json=p2, headers=headers)
    assert r2.status_code == 409
    assert "PLT-002" in r2.text


@pytest.mark.invariants
async def test_swap_base_atomic(client, setup_company):
    # SPEC-001 R6: cambiar is_base atómicamente demota la actual base
    headers = {"language": "es", "timezone": "America/Bogota"}

    p1 = {"company_id": setup_company["company_id"], "currency_id": setup_company["currency_a"], "is_base": True}
    r1 = await client.post("/company-currency", json=p1, headers=headers)
    assert r1.status_code == 200
    cc_a_id = r1.json()["response"]["id"]

    p2 = {"company_id": setup_company["company_id"], "currency_id": setup_company["currency_b"], "is_base": False}
    r2 = await client.post("/company-currency", json=p2, headers=headers)
    assert r2.status_code == 200
    cc_b_id = r2.json()["response"]["id"]

    update_payload = {"id": cc_b_id, "is_base": True}
    r3 = await client.put("/company-currency", json=update_payload, headers=headers)
    assert r3.status_code == 200

    list_payload = {"all_data": True, "filters": [{"field": "company_id", "condition": "==", "value": setup_company["company_id"]}]}
    r4 = await client.post("/company-currency/list", json=list_payload, headers=headers)
    assert r4.status_code == 200
    rows = r4.json()["response"]
    bases = [r for r in rows if r.get("is_base")]
    assert len(bases) == 1
    assert bases[0]["id"] == cc_b_id


async def test_delete_only_base_rejected(client, setup_company):
    # SPEC-001 PLT-003: no se puede borrar la única company_currency cuando es base
    headers = {"language": "es", "timezone": "America/Bogota"}
    p1 = {"company_id": setup_company["company_id"], "currency_id": setup_company["currency_a"], "is_base": True}
    r1 = await client.post("/company-currency", json=p1, headers=headers)
    assert r1.status_code == 200
    cc_id = r1.json()["response"]["id"]

    r2 = await client.delete(f"/company-currency/{cc_id}", headers=headers)
    assert r2.status_code == 409
    assert "PLT-003" in r2.text
