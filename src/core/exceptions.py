"""
SPEC-001 T4 — Excepciones de negocio del dominio platform.

`BusinessException` permite que los UCs/repos levanten errores de business rule
con códigos `PLT-NNN` traducibles, en lugar de `ValueError` genéricos que
salen al cliente como HTTP 500/400 sin contexto.

`execute_transaction` traduce `BusinessException` a HTTP 409 con el código y
key apropiados; el cliente luego resuelve el mensaje localizado vía la tabla
`translation`.
"""


class BusinessException(Exception):
    """Excepción levantada por business rule violations.

    Attributes:
        key: KEYS_MESSAGES enum value (ej. "plt_company_currency_not_found")
             usado para traducir a mensaje localizado vía la tabla `translation`.
        code: Código alfanumérico (ej. "PLT-001") devuelto al cliente en
              el campo `code` del `Response`. Opcional — si None, el handler
              puede buscar el código asociado al `key` en la tabla `translation`.
    """

    def __init__(self, key: str, code: str | None = None):
        self.key = key
        self.code = code
        super().__init__(key)
