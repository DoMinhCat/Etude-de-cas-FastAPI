from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError
from sqlalchemy import select, func

from app.core.security import decode_access_token
from app.models.client import Client

# Point d'extension pour la DB (session SQLAlchemy), à brancher quand vous implémentez.
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        org_id = payload.get("org_id")
        if username is None or org_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    result = await db.execute(
        select(Client).filter(func.lower(Client.username) == username.lower())
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # attacher org_id du token
    user.org_id = org_id 
    return user

def get_org_id(x_org_id: str | None = Header(default=None, alias="X-Org-ID")) -> str:
    """Header obligatoire pour toutes les routes (hors /health).
    TODO (bonus): dériver l'org depuis un token (auth) plutôt que depuis un header.
    """
    if not x_org_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Org-ID required")
    return x_org_id

