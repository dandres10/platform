from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from limits import parse
from limits.strategies import FixedWindowRateLimiter
from limits.storage import MemoryStorage
from src.core.classes.token import Token

# SPEC-020
BUSINESS_PREFIXES = (
    "/auth/",
    "/catalog/",
    "/geography/",
)
EXEMPT_PREFIXES = ("/health", "/mcp", "/docs", "/openapi.json", "/redoc")


class UserRateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.storage = MemoryStorage()
        self.limiter = FixedWindowRateLimiter(self.storage)
        self.business_rate = parse("30/minute")
        self.entity_rate = parse("60/minute")
        self.read_rate = parse("120/minute")

    def _get_user_key(self, request: Request) -> str:
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            try:
                token = Token().verify_token(token=authorization.split(" ")[1])
                return token.user_id
            except Exception:
                pass
        return request.client.host if request.client else "unknown"

    def _classify(self, path: str, method: str) -> str:
        clean_path = path.replace("/v1", "", 1) if path.startswith("/v1/") else path

        if any(clean_path.startswith(p) for p in EXEMPT_PREFIXES):
            return "exempt"
        if any(clean_path.startswith(p) for p in BUSINESS_PREFIXES):
            if method in ("POST", "PUT", "DELETE"):
                return "business"
            return "read"
        if method in ("POST", "PUT", "DELETE"):
            return "entity"
        return "read"

    def _get_rate(self, category: str):
        if category == "business":
            return self.business_rate
        elif category == "entity":
            return self.entity_rate
        return self.read_rate

    async def dispatch(self, request: Request, call_next):
        category = self._classify(request.url.path, request.method)

        if category == "exempt":
            return await call_next(request)

        user_key = self._get_user_key(request)
        rate = self._get_rate(category)
        key = f"{user_key}:{request.url.path}"

        if not self.limiter.hit(rate, key):
            return JSONResponse(
                status_code=429,
                content={
                    "message_type": "STATIC",
                    "notification_type": "ERROR",
                    "message": "Rate limit exceeded. Please try again later.",
                    "code": "RATE-001",
                    "response": None,
                },
            )

        return await call_next(request)
