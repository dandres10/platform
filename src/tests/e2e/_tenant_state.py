# SPEC-003 T3
from contextlib import contextmanager
from uuid import uuid4


_ACTIVE: dict = {}


def init(company_id: str, user_id: str, rol_code: str = "ADMIN") -> None:
    _ACTIVE["company_id"] = company_id
    _ACTIVE["user_id"] = user_id
    _ACTIVE["rol_code"] = rol_code


def current_company_id() -> str:
    return _ACTIVE["company_id"]


def current_user_id() -> str:
    return _ACTIVE["user_id"]


def current_rol_code() -> str:
    return _ACTIVE.get("rol_code", "ADMIN")


@contextmanager
def switch_tenant(company_id: str, user_id: str = None):
    prev_c = _ACTIVE.get("company_id")
    prev_u = _ACTIVE.get("user_id")
    _ACTIVE["company_id"] = company_id
    _ACTIVE["user_id"] = user_id or str(uuid4())
    try:
        yield
    finally:
        _ACTIVE["company_id"] = prev_c
        _ACTIVE["user_id"] = prev_u


@contextmanager
def switch_role(rol_code: str):
    prev = _ACTIVE.get("rol_code", "ADMIN")
    _ACTIVE["rol_code"] = rol_code
    try:
        yield
    finally:
        _ACTIVE["rol_code"] = prev
