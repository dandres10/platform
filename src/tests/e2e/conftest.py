# SPEC-003 T4
import os
import warnings
import pytest
import pytest_asyncio
import httpx
from uuid import uuid4
from contextlib import asynccontextmanager
from fastapi import Request
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.core.enums.permission_type import PERMISSION_TYPE
from src.core.models.config import Config
from src.core.models.access_token import AccessToken
from src.tests.e2e import _tenant_state


COMPANY_ID = str(uuid4())
USER_ID = str(uuid4())
OTHER_COMPANY_ID = str(uuid4())

_tenant_state.init(COMPANY_ID, USER_ID)

# SPEC-003 T9: forzar has_track=True en tests para que execute_transaction
# capture BusinessException y la traduzca a HTTPException 409.
from src.core.config import settings as _settings
_settings.has_track = True


def _make_token(company_id: str, user_id: str, rol_code: str = None) -> AccessToken:
    effective_role = rol_code or _tenant_state.current_rol_code()
    return AccessToken(
        rol_id=str(uuid4()),
        rol_code=effective_role,
        user_id=user_id,
        location_id=str(uuid4()),
        currency_id=str(uuid4()),
        company_id=company_id,
        token_expiration_minutes=60,
        permissions=[p.value for p in PERMISSION_TYPE],
    )


def _rebuild_engine():
    import src.infrastructure.database.config.async_config_db as db_module

    new_engine = create_async_engine(
        db_module.string_db,
        pool_size=15,
        max_overflow=10,
        pool_timeout=10,
        pool_recycle=3600,
        echo=False,
    )
    new_async_db = async_sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        bind=new_engine,
        class_=AsyncSession,
    )

    @asynccontextmanager
    async def new_async_session_db():
        async with new_async_db() as session:
            yield session

    db_module.engine = new_engine
    db_module.async_db = new_async_db
    db_module.async_session_db = new_async_session_db

    return new_engine


_test_engine = None


async def get_e2e_config(request: Request):
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.models.filter import Pagination, FilterManager

    config = Config()
    config.token = _make_token(
        company_id=_tenant_state.current_company_id(),
        user_id=_tenant_state.current_user_id(),
    )
    config.language = "es"
    config.timezone = "America/Bogota"
    config.response_type = "dict"
    config.request = request

    qp = request.query_params
    if "skip" in qp or "limit" in qp or "all_data" in qp or "filter" in qp:
        raw_filters = qp.getlist("filter")
        filters = []
        for raw in raw_filters:
            parts = raw.split(",", 2)
            if len(parts) == 3:
                filters.append(FilterManager(field=parts[0], condition=parts[1], value=parts[2]))
        config.pagination = Pagination(
            skip=int(qp.get("skip", 0)),
            limit=int(qp.get("limit", 50)),
            all_data=qp.get("all_data", "false").lower() == "true",
            filters=filters if filters else None,
        )

    async with async_session_db() as session:
        config.async_db = session
        yield config


async def _cleanup_test_data(engine, company_id: str):
    from src.core.config import settings
    s = settings.database_schema

    # SPEC-003 T4: tablas hijas via FK al padre (orden: hijos primero)
    child_tables = [
        ("rol_permission", "rol_id", "rol"),
        ("menu_permission", "menu_id", "menu"),
        ("api_token", "rol_id", "rol"),
        ("user_location_rol", "location_id", "location"),
        ("currency_location", "location_id", "location"),
    ]

    # SPEC-003 T4: user_country via user via platform via location
    user_country_via_user = (
        "user_country", "user_id",
        f'(SELECT u.id FROM {s}."user" u JOIN {s}."platform" p ON u.platform_id = p.id '
        f'JOIN {s}."location" l ON p.location_id = l.id WHERE l.company_id = :cid)'
    )

    # SPEC-003 T4: user via platform via location
    user_via_platform = (
        "user", "platform_id",
        f'(SELECT p.id FROM {s}."platform" p JOIN {s}."location" l ON p.location_id = l.id WHERE l.company_id = :cid)'
    )

    # SPEC-003 T4: platform via location
    platform_via_location = (
        "platform", "location_id",
        f'(SELECT id FROM {s}."location" WHERE company_id = :cid)'
    )

    # SPEC-003 T4: tablas con company_id directo (orden: hijos → padres)
    direct = [
        "menu",
        "permission",
        "rol",
        "company_currency",
        "location",
    ]

    async with engine.begin() as conn:
        for child, fk_col, parent in child_tables:
            try:
                await conn.execute(text(
                    f'DELETE FROM {s}."{child}" WHERE {fk_col} IN '
                    f'(SELECT id FROM {s}."{parent}" WHERE company_id = :cid)'
                ), {"cid": company_id})
            except Exception:
                pass

        for tbl, fk_col, subq in [user_country_via_user, user_via_platform, platform_via_location]:
            try:
                await conn.execute(
                    text(f'DELETE FROM {s}."{tbl}" WHERE {fk_col} IN {subq}'),
                    {"cid": company_id},
                )
            except Exception:
                pass

        for table in direct:
            try:
                await conn.execute(
                    text(f'DELETE FROM {s}."{table}" WHERE company_id = :cid'),
                    {"cid": company_id},
                )
            except Exception:
                pass

        try:
            await conn.execute(
                text(f'DELETE FROM {s}."company" WHERE id = :cid'),
                {"cid": company_id},
            )
        except Exception:
            pass


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def client():
    global _test_engine
    _test_engine = _rebuild_engine()

    from main import app
    from src.core.methods.get_config import get_config

    app.dependency_overrides[get_config] = get_e2e_config

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c

    await _cleanup_test_data(_test_engine, COMPANY_ID)
    await _cleanup_test_data(_test_engine, OTHER_COMPANY_ID)

    app.dependency_overrides.clear()
    await _test_engine.dispose()


@pytest.fixture(scope="session")
def company_id():
    return COMPANY_ID


@pytest.fixture(scope="session")
def other_company_id():
    return OTHER_COMPANY_ID


def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "invariants: run invariant check after this test (opt-in, slow)",
    )
    config.addinivalue_line(
        "markers",
        "no_invariants: test intentionally leaves inconsistent state",
    )


@pytest_asyncio.fixture(autouse=True, loop_scope="session")
async def _assert_invariants(request, client):
    yield
    if request.node.get_closest_marker("no_invariants"):
        return
    strict = request.node.get_closest_marker("invariants") is not None
    reporter = os.getenv("INVARIANTS") == "1"
    if not (strict or reporter):
        return
    from src.tests.e2e._invariants import run_all
    violations = await run_all(_test_engine, [COMPANY_ID, OTHER_COMPANY_ID])
    if not violations:
        return
    message = (
        f"SPEC-003 invariant violations after {request.node.nodeid}:\n  "
        + "\n  ".join(violations)
    )
    if strict:
        assert False, message
    else:
        warnings.warn(message, stacklevel=2)


# SPEC-032 T1
@pytest_asyncio.fixture(scope="function")
async def seed_authenticated_external_user(client):
    """User externo con refresh_token poblado (sesión activa) + override
    _tenant_state.user_id/rol_code='USER' para que el config sintético del
    conftest apunte al user seedeado. Restaura state previo en cleanup."""
    from src.infrastructure.database.config.async_config_db import async_session_db
    from src.core.config import settings
    from src.core.classes.password import Password
    from src.tests.e2e import _tenant_state
    s = settings.database_schema

    user_id = uuid4()
    platform_id = uuid4()
    ulr_id = uuid4()
    email = f"e2e-auth-{str(uuid4())[:8]}@test.com"
    password = "Test1234!"
    fake_refresh = f"fake-refresh-{uuid4().hex}"

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
            VALUES (:uid, :pid, :email, :pwd, :ident, 'E2E', 'Test', '+57 123', :rt, true)
        """), {
            "uid": user_id, "pid": platform_id, "email": email,
            "pwd": Password.hash_password(password=password),
            "ident": f"E2E-{str(uuid4())[:8]}",
            "rt": fake_refresh,
        })

        await session.execute(text(f"""
            INSERT INTO {s}."user_location_rol" (id, user_id, location_id, rol_id, state)
            VALUES (:ulr, :uid, NULL, :rol, true)
        """), {"ulr": ulr_id, "uid": user_id, "rol": rol_user})
        await session.commit()

    prev_user = _tenant_state._ACTIVE.get("user_id")
    prev_role = _tenant_state._ACTIVE.get("rol_code", "ADMIN")
    _tenant_state._ACTIVE["user_id"] = str(user_id)
    _tenant_state._ACTIVE["rol_code"] = "USER"

    yield {
        "email": email,
        "password": password,
        "user_id": str(user_id),
        "refresh_token": fake_refresh,
    }

    _tenant_state._ACTIVE["user_id"] = prev_user
    _tenant_state._ACTIVE["rol_code"] = prev_role

    async with async_session_db() as session:
        await session.execute(text(f'DELETE FROM {s}."password_reset_token" WHERE user_id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."user_location_rol" WHERE user_id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."user" WHERE id = :uid'), {"uid": user_id})
        await session.execute(text(f'DELETE FROM {s}."platform" WHERE id = :pid'), {"pid": platform_id})
        await session.commit()
