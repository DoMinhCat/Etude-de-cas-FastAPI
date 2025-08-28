from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_

from app.api.deps import get_org_id
from app.api.deps import get_current_user, get_db
from app.schemas.tech import TechOut, CreateTech
from app.models.technician import Technician
from app.models.client import Client

router = APIRouter(prefix="/technicians", tags=["technicians"])

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

@router.get("")
def list_technicians(q: str | None = None, limit: int = 50, offset: int = 0, org: str = Depends(get_org_id)):
    """Lister techniciens (org).
    TODO: filtre q (nom/email), pagination.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement list_technicians")

@router.get("/{tech_id}")
def get_technician(tech_id: int, org: str = Depends(get_org_id)):
    """Récupérer technicien (org)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement get_technician")

@router.patch("/{tech_id}")
def update_technician(tech_id: int, org: str = Depends(get_org_id)):
    """PATCH technicien."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement update_technician")

@router.delete("/{tech_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_technician(tech_id: int, org: str = Depends(get_org_id)):
    """Supprimer technicien (soft/hard)."""
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement delete_technician")
