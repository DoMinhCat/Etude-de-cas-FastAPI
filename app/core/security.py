from fastapi import Request
from passlib.context import CryptContext
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timezone, timedelta
from typing import Any, Dict

from app.core.config import settings

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

# JWT
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
TOKEN_EXPIRE_MINUTES = int(settings.TOKEN_EXPIRES_MINUTES)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

