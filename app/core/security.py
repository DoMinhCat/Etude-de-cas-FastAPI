from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Headers de sécurité basiques.
    TODO (bonus): CSP, autres policies, etc.
    """
    async def dispatch(self, request: Request, call_next):
        resp = await call_next(request)
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["Referrer-Policy"] = "no-referrer"
        resp.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        resp.headers["Permissions-Policy"] = "geolocation=()"
        return resp
