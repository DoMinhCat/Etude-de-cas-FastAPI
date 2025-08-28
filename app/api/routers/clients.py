from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from typing import List

from app.api.deps import get_org_id, get_db, get_current_user
from app.models.client import Client
from app.schemas.client import PaginatedClient, ClientOut

router = APIRouter(prefix="/clients", tags=["clients"])

default_limit = 50
max_limit = 200

@router.post("", status_code=status.HTTP_201_CREATED)
def create_client(org: str = Depends(get_org_id)):
    """Créer un client (org courante).
    TODO: définir schémas Pydantic, insérer en base (filtré org), gérer validations & erreurs.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement create_client")

@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedClient)
def list_clients(
    q: str | None = None,
    limit: int = default_limit,
    offset: int = 0,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister clients de l'org (pagination & filtre q).
    TODO: requête SQL (limit/offset), recherche q (au choix: name/email), retour liste (+ total si voulu).
    """

    if limit < 1 or limit > max_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Limit doit être entre 1 et {max_limit}.")
    if offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offset ne peut pas être négatif.")
    
    query = select(Client).filter(Client.org_id == current_user.org_id)

    # Filtre
    if q:
        search = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Client.first_name).like(search),
                func.lower(Client.last_name).like(search),
                func.lower(Client.email).like(search)
            )
        )
    # Total number of results before offset or limit
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    query = query.limit(limit).offset(offset)

    try:
        clients = db.execute(query).scalars().all()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur serveur imprévue.")
    
    if not clients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Aucun client trouvé pour cette organisation.")
    
    return PaginatedClient(
        total_result=total,
        limit=limit,
        offset=offset,
        clients=[ClientOut.model_validate(c, from_attributes=True) for c in clients]
    )

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
