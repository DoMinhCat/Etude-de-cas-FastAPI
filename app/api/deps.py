from fastapi import Depends, Header, HTTPException, status

def get_org_id(x_org_id: str | None = Header(default=None, alias="X-Org-ID")) -> str:
    """Header obligatoire pour toutes les routes (hors /health).
    TODO (bonus): dériver l'org depuis un token (auth) plutôt que depuis un header.
    """
    if not x_org_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="X-Org-ID required")
    return x_org_id

# Point d'extension pour la DB (session SQLAlchemy), à brancher quand vous implémentez.
from app.db.session import get_db
