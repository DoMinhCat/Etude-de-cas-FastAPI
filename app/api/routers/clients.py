from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.api.deps import get_org_id, get_db, get_current_user
from app.models.client import Client

router = APIRouter(prefix="/clients", tags=["clients"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_client(org: str = Depends(get_org_id)):
    """Créer un client (org courante).
    TODO: définir schémas Pydantic, insérer en base (filtré org), gérer validations & erreurs.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement create_client")

@router.get("")
async def list_clients(q: str | None = None, limit: int = 50, offset: int = 0, org: str = Depends(get_org_id),
                 current_user = Depends(get_current_user),
                 db: AsyncSession = Depends(get_db)):
    """Lister clients de l'org (pagination & filtre q).
    TODO: requête SQL (limit/offset), recherche q (au choix: name/email), retour liste (+ total si voulu).
    """
    result = await db.execute(select(Client).filter(Client.org_id == org))
    clients = result.scalars().all()
    return clients

@router.get("/{client_id}")
def get_client(client_id: int, org: str = Depends(get_org_id)):
    """Récupérer un client (filtré org).
    TODO: SELECT + 404 si introuvable/hors org.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement get_client")

@router.patch("/{client_id}")
def update_client(client_id: int, org: str = Depends(get_org_id)):
    """PATCH partiel client.
    TODO: schéma PATCH, appliquer champs présents, validations.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement update_client")

@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(client_id: int, org: str = Depends(get_org_id)):
    """Supprimer client.
    TODO: soft-delete (deleted_at) recommandé OU hard delete (documentez), vérifier appartenance org.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement delete_client")
