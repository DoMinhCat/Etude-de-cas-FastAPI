from fastapi import APIRouter, Depends, HTTPException, status
from app.api.deps import get_org_id

router = APIRouter(prefix="/interventions/{intervention_id}/events", tags=["events"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(intervention_id: int, org: str = Depends(get_org_id)):
    """Ajouter un évènement à la timeline d'un intervention.
    TODO: types d'évènements (enum libre), payload (note, JSON...), vérifier intervention ∈ org, insert + horodatage.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement create_event")

@router.get("")
def list_events(intervention_id: int, org: str = Depends(get_org_id)):
    """Lister la timeline d'un intervention (ordre chronologique).
    TODO: SELECT events par intervention_id/org, ORDER BY date ASC.
    """
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Implement list_events")
