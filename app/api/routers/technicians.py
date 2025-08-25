from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_org_id

router = APIRouter(prefix="/technicians", tags=["technicians"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_technician(org: str = Depends(get_org_id)):
    """Créer technicien (org).
    TODO: schémas, unicité éventuelle (email/org), insert, erreurs.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement create_technician")

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
