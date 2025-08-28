from fastapi import Depends, Header, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from sqlalchemy import select, func
from typing import Literal

from app.core.security import decode_access_token
from app.models.client import Client
from app.models.technician import Technician

# Point d'extension pour la DB (session SQLAlchemy), à brancher quand vous implémentez.
from app.db.session import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        org_id = payload.get("org_id")
        role = payload.get("role")

        if username is None or org_id is None:
            raise HTTPException(status_code=401, detail="Token invalide")
        
        if role == "client":
            query = select(Client).filter(func.lower(Client.username) == username.lower())
        elif role == "tech":
            query = select(Technician).filter(func.lower(Technician.username) == username.lower())
        else:
            raise HTTPException(status_code=403, detail="Rôle inconnu.")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")

    result = db.execute(query).scalars().first()
    if not result:
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé.")
    
    # attacher org_id du token
    result.org_id = org_id 
    result.role = role
    return result

def get_org_id(x_org_id: str | None = Header(default=None, alias="X-Org-ID")) -> str:
    """Header obligatoire pour toutes les routes (hors /health).
    TODO (bonus): dériver l'org depuis un token (auth) plutôt que depuis un header.
    """
    if not x_org_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Org-ID required")
    return x_org_id

def get_role(expected_role: Literal["client", "tech"] = "client"):
    def role_checker(user = Depends(get_current_user)):
        if user.role != expected_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Accès interdit, rôle requis : {expected_role}"
            )
        return user
    return role_checker

