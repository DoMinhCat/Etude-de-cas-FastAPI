from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List, Any
import enum

class EventType(str, enum.Enum):
    STARTED = "started"
    UPDATED = "updated"
    COMPLETED = "completed"
    DELETED = "deleted"

class CreateEvent(BaseModel):
    type: Optional[EventType] = EventType.STARTED
    note: Optional[str] = None
    tech_id: int | None = None
    payload: Optional[dict[str, Any]] = None

class EventOut(BaseModel):
    id: int
    type: str
    note: Optional[str] = None
    payload: Optional[dict[str, Any]] = None
    created_at: datetime

    intervention_id: int
    organisation: str
    technician_id: Optional[int] = None

    class Config:
        model_config = {
            'from_attributes': True,
            'extra': 'ignore'
        }
