from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.api.deps import get_current_user, get_role, get_db, get_org_id
from app.models.intervention import Intervention
from app.models.client import Client
from app.models.technician import Technician
from app.models.organisation import Organisation
from app.schemas.intervention import CreateItem, PaginatedItem, ItemOut

router = APIRouter(prefix="/items", tags=["items"])

default_limit = 50
max_limit = 200

@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(
    new_item: CreateItem,
    current_user: Client = Depends(get_current_user),
    current_role = Depends(get_role("tech")),
    db: Session = Depends(get_db)
):
    """Créer un item (intervention/ticket) pour un client de l'org.
    TODO: payload (client_id, title...), vérifier que le client ∈ org, statut initial (enum libre), insert.
    """

    client = db.execute(
        select(Client).filter(Client.id == new_item.client_id, Client.org_id == current_user.org_id)
    ).scalars().first()
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable dans votre organisation.")
    
    technician = db.execute(
        select(Technician).filter(Technician.id == new_item.technician_id, Technician.org_id == current_user.org_id)
    ).scalars().first()
    if not technician:
        raise HTTPException(status_code=404, detail="Technicien assigné introuvable dans votre organisation.")
    
    item = Intervention(
        client_id=client.id,
        organisation_id=current_user.org_id,
        technician_id=technician.id,
        description=new_item.description,
        status=new_item.status
    )

    try:
        db.add(item)
        db.commit()
        db.refresh(item)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur imprévue lors de la création de l'intervention. {e}"
        )
    
    return {"message": f"Nouvelle intervention id : {item.id} créée avec succès."}

@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedItem)
def list_items(
    status_eq: str | None = None,
    client_id: int | None = None,
    q: str | None = None,
    limit: int = default_limit,
    offset: int = 0,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister items (org).
    TODO: filtres (status, client_id, q - username client/technicien), pagination.
    """
    
    if limit < 1 or limit > max_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Limit doit être entre 1 et {max_limit}.")
    if offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offset ne peut pas être négatif.")
    
    query = (
    select(
        Intervention,
        Organisation.name.label("org_name"),
        Client.username.label("client_username"),
        Technician.username.label("technician_username")
    )
    .join(Organisation, Intervention.organisation_id == Organisation.id)
    .join(Client, Intervention.client_id == Client.id)
    .join(Technician, Intervention.technician_id == Technician.id)
    .filter(Intervention.organisation_id == current_user.org_id)
    )

    # Filtre
    if q:
        search = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Technician.username).like(search),
                func.lower(Client.username).like(search)               
            )
        )

    if status_eq:
        search = f"%{status_eq.lower()}%"
        query = query.filter(func.lower(Intervention.status).like(search))

    if client_id:
        query = query.filter(Intervention.client_id == client_id)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    query = query.limit(limit).offset(offset)

    try:
        rows = db.execute(query).all()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur serveur imprévue.")
    
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Aucune intervention trouvée pour votre organisation.")
    
    items = [
        ItemOut(
            id=row.Intervention.id, status=row.Intervention.status, description=row.Intervention.description,
            client_username=row.client_username, technicien_username=row.technician_username, organisation=row.org_name, created_at=row.Intervention.created_at, updated_at=row.Intervention.updated_at, deleted_at=row.Intervention.deleted_at
        ) for row in rows
    ]
    return PaginatedItem(
        total_result=total,
        limit=limit,
        offset=offset,
        interventions=items
    )

@router.get("/{item_id}")
def get_item(item_id: int, org: str = Depends(get_org_id)):
    """Récupérer item (org)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement get_item")

@router.patch("/{item_id}")
def update_item(item_id: int, org: str = Depends(get_org_id)):
    """PATCH item (title/status/description...).
    TODO: définir règles de transition de statut; retourner 409 si invalide.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement update_item")

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, org: str = Depends(get_org_id)):
    """Supprimer item (soft/hard).
    TODO: soft-delete recommandé (deleted_at).
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement delete_item")
