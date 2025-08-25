from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_org_id

router = APIRouter(prefix="/items", tags=["items"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_item(org: str = Depends(get_org_id)):
    """Créer un item (intervention/ticket) pour un client de l'org.
    TODO: payload (client_id, title...), vérifier que le client ∈ org, statut initial (enum libre), insert.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement create_item")

@router.get("")
def list_items(
    status_eq: str | None = None,
    client_id: int | None = None,
    q: str | None = None,
    limit: int = 50,
    offset: int = 0,
    org: str = Depends(get_org_id),
):
    """Lister items (org).
    TODO: filtres (status, client_id, q), pagination.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement list_items")

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
