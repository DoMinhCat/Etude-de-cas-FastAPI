from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.api.deps import get_org_id
from app.api.deps import get_current_user, get_db
from app.schemas.tech import TechOut, CreateTech, PaginatedTech
from app.models.technician import Technician
from app.models.organisation import Organisation
from app.models.client import Client

router = APIRouter(prefix="/technicians", tags=["technicians"])

default_limit = 50
max_limit = 200

@router.post("", status_code=status.HTTP_201_CREATED)
def create_technician(
    new_tech: CreateTech,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer technicien (org).
    TODO: schémas, unicité éventuelle (email/org), insert, erreurs.
    """
    
    query = select(Technician).filter(Technician.org_id == current_user.org_id)

    check_query = query.filter(func.lower(Technician.email) == new_tech.email.lower())
    db_tech = db.execute(check_query).scalars().first()
    if db_tech:
        raise HTTPException(status_code=400, detail="Cette adresse email est déjà inscrite. Veuillez choisir une autre adresse.")

    tech_to_add = Technician(name=new_tech.name, email=new_tech.email, org_id=current_user.org_id)
    try:
        db.add(tech_to_add)
        db.commit()
        db.refresh(tech_to_add)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur imprévue lors de la création du technicien."
        )
    
    return {"message": f"Nouveau technicien '{new_tech.name}' créé avec succès."}

@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedTech)
def list_technicians(
    q: str | None = None, 
    limit: int = default_limit, 
    offset: int = 0, 
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)):
    """Lister techniciens (org).
    TODO: filtre q (nom/email), pagination.
    """

    if limit < 1 or limit > max_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Limit doit être entre 1 et {max_limit}.")
    if offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offset ne peut pas être négatif.")
    
    query = (
    select(Technician, Organisation.name.label("org_name"))
    .join(Organisation, Technician.org_id == Organisation.id)
    .filter(Technician.org_id == current_user.org_id)   
    )

    # Filtre
    if q:
        search = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Technician.name).like(search),
                func.lower(Technician.email).like(search)
            )
        )
    # Total number of results before offset or limit
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    query = query.limit(limit).offset(offset)
    
    try:
        rows = db.execute(query).all()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur serveur imprévue.")
    
    if not rows:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Aucun technicien trouvé pour votre organisation.")
    
    techniciens = [
        TechOut(name=row.Technician.name, email=row.Technician.email, organisation=row.org_name)
        for row in rows
    ]
    return PaginatedTech(
        total_result=total,
        limit=limit,
        offset=offset,
        techniciens=techniciens
    )
    
@router.get("/{tech_id}", status_code=status.HTTP_200_OK, response_model=TechOut)
def get_technician(
    tech_id: int,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db) 
    ):
    """Récupérer technicien (org)."""

    query = (
    select(Technician, Organisation.name.label("org_name"))
    .join(Organisation, Technician.org_id == Organisation.id)
    .filter(current_user.org_id == Technician.org_id, tech_id == Technician.id)   
    )
    row = db.execute(query).first()

    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client avec id {tech_id} introuvable dans votre organisation.")
    
    technicien = TechOut(
        id=row.Technician.id,
        name=row.Technician.name,
        email=row.Technician.email,
        organisation=row.org_name
    )
    return technicien

@router.patch("/{tech_id}")
def update_technician(tech_id: int, org: str = Depends(get_org_id)):
    """PATCH technicien."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement update_technician")

@router.delete("/{tech_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_technician(tech_id: int, org: str = Depends(get_org_id)):
    """Supprimer technicien (soft/hard)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement delete_technician")
