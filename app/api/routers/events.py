from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from datetime import datetime, timezone
from typing import List

from app.api.deps import get_org_id, get_current_user, get_db, get_role
from app.models.client import Client
from app.models.organisation import Organisation
from app.models.technician import Technician
from app.models.event import Event
from app.models.intervention import Intervention
from app.schemas.event import CreateEvent, EventOut

router = APIRouter(prefix="/interventions/{intervention_id}/events", tags=["events"])

@router.post("", status_code=status.HTTP_201_CREATED)
def create_event(
    new_event: CreateEvent,
    intervention_id: int, 
    current_user: Client = Depends(get_current_user),
    current_role = Depends(get_role("tech")),
    db: Session = Depends(get_db)
    ):
    """Ajouter un évènement à la timeline d'un intervention.
    TODO: types d'évènements (enum libre), payload (note, JSON...), vérifier intervention ∈ org, insert + horodatage.
    """
    
    intervention = db.query(Intervention).filter(
        Intervention.id == intervention_id,
        Intervention.org_id == current_user.org_id
    ).first()
    if not intervention:
        raise HTTPException(status_code=404, detail="Intervention introuvable dans votre organisation.")
    if intervention.deleted_at is not None:
        raise HTTPException(status_code=409, detail="Cette intervention est déjà supprimée.")
    
    tech_id = new_event.tech_id

    if new_event.tech_id == 0:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technicien introuvable dans votre organisation ou supprimé."
            )
    
    if tech_id:
        tech = (
            db.query(Technician)
            .filter(
                Technician.id == tech_id,
                Technician.org_id == intervention.org_id,
                Technician.deleted_at.is_(None)   # soft delete check
            )
            .first()
        )

        if not tech:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Technicien introuvable dans votre organisation ou supprimé."
            )

    event = Event(
        type=new_event.type,
        note=new_event.note,
        payload=new_event.payload,
        intervention_id=intervention_id,
        organisation_id=current_user.org_id,
        technician_id=new_event.tech_id,   
        created_at=datetime.now(timezone.utc)
    )

    try:
        db.add(event)
        db.commit()
        db.refresh(event)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur serveur imprévue lors de la création d'évènement. {e}"
        )
    
    return {"message": f"Nouvelle intervention id : {event.id} créée avec succès."}

@router.get("", status_code=status.HTTP_200_OK, response_model=List[EventOut])
def list_events(
    intervention_id: int,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """Lister la timeline d'un intervention (ordre chronologique).
    TODO: SELECT events par intervention_id/org, ORDER BY date ASC.
    """
    
    intervention = db.execute(
        select(Intervention)
        .filter(
            Intervention.id == intervention_id,
            Intervention.org_id == current_user.org_id
        )
    ).scalars().first()

    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Intervention introuvable dans votre organisation."
        )
    
    query = (
    db.query(Event.id, Event.type, Event.note, Event.payload,
             Event.created_at, Event.intervention_id,
             Organisation.name.label("organisation"),
             Event.technician_id)
            .join(Organisation, Organisation.id == Event.organisation_id)
            .filter(Event.intervention_id == intervention_id)
            .order_by(Event.created_at.asc())
    )
    events = query.all()
    return events