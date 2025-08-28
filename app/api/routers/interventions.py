from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from datetime import datetime, timezone

from app.api.deps import get_current_user, get_role, get_db
from app.models.intervention import Intervention
from app.models.client import Client
from app.models.technician import Technician
from app.models.organisation import Organisation
from app.schemas.intervention import CreateItem, PaginatedItem, ItemOut, PatchItem, InterventionStatus

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
    current_role = Depends(get_role("tech")),
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
    .join(Organisation, Intervention.org_id == Organisation.id)
    .join(Client, Intervention.client_id == Client.id)
    .join(Technician, Intervention.technician_id == Technician.id)
    .filter(Intervention.org_id == current_user.org_id)
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

@router.get("/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemOut)
def get_item(
    item_id: int,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db) 
    ):
    """Récupérer item (org)."""
    
    query = (
    select(
        Intervention,
        Organisation.name.label("org_name"),
        Client.username.label("client_username"),
        Technician.username.label("technician_username")
    )
    .join(Organisation, Intervention.org_id == Organisation.id)
    .join(Client, Intervention.client_id == Client.id)
    .join(Technician, Intervention.technician_id == Technician.id)
    .filter(Intervention.org_id == current_user.org_id, item_id == Intervention.id)
    )
    row = db.execute(query).first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Technicien avec id {item_id} introuvable dans votre organisation.")
    
    item = ItemOut(
    id=row.Intervention.id,
    status=row.Intervention.status,
    description=row.Intervention.description,
    client_username=row.client_username,
    technicien_username=row.technician_username,
    organisation=row.org_name,
    created_at=row.Intervention.created_at,
    updated_at=row.Intervention.updated_at,
    deleted_at=row.Intervention.deleted_at
    )
    return item

@router.patch("/{item_id}", status_code=status.HTTP_200_OK, response_model=ItemOut)
def update_item(
    item_id: int,
    patch_data: PatchItem,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user),
    current_role = Depends(get_role("tech"))
    ):
    """PATCH item (title/status/description...).
    TODO: définir règles de transition de statut; retourner 409 si invalide.
    """
    
    intervention = db.execute(
        select(Intervention)
        .filter(
            Intervention.id == item_id,
            Intervention.org_id == current_user.org_id
        )
    ).scalars().first()

    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention introuvable dans votre organisation.")
    if intervention.deleted_at is not None:
        raise HTTPException(status_code=409, detail="Cette intervention est déjà supprimée.")
    
    if patch_data.status:
        current_status = intervention.status
        new_status = patch_data.status

        valid_transitions = {
            InterventionStatus.PENDING: [InterventionStatus.IN_PROGRESS, InterventionStatus.CANCELLED],
            InterventionStatus.IN_PROGRESS: [InterventionStatus.COMPLETED, InterventionStatus.CANCELLED],
            InterventionStatus.COMPLETED: [InterventionStatus.CANCELLED],
            InterventionStatus.CANCELLED: []
        }

        if new_status != InterventionStatus.CANCELLED and new_status not in valid_transitions[current_status]:
            raise HTTPException(
                status_code=409,
                detail=f"Transition de statut invalide: {current_status.value} → {new_status.value}"
            )

        intervention.status = new_status

    if patch_data.description is not None:
        intervention.description = patch_data.description

    try:
        db.commit()
        db.refresh(intervention)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur serveur imprévue lors de la mise à jour de l'intervention."
        )

    client_username = intervention.client.username
    technician_username = intervention.technician.username
    organisation_name = intervention.organisation.name

    return ItemOut(
        id=intervention.id,
        status=intervention.status,
        description=intervention.description,
        client_username=client_username,
        technicien_username=technician_username,
        organisation=organisation_name,
        created_at=intervention.created_at,
        updated_at=intervention.updated_at,
        deleted_at=intervention.deleted_at
    )

@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user),
    current_role = Depends(get_role("tech"))
    ):
    """Supprimer item (soft/hard).
    TODO: soft-delete recommandé (deleted_at).
    """
    
    item = db.execute(
        select(Intervention).filter(Intervention.id == item_id, Intervention.org_id == current_user.org_id)
    ).scalars().first()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervention avec id {item_id} introuvable dans votre organisation."
        )
    
    if item.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Intervention déjà supprimée."
        )
    
    item.deleted_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur imprévue lors de la suppression de l'intervention."
        )

    return {"message" : "Intervention supprimé avec succès."}