from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional, List
import enum

class InterventionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class CreateItem(BaseModel):
    status: Optional[InterventionStatus] = InterventionStatus.PENDING
    description: Optional[str] = None
    client_id: int
    technician_id: int

class ItemOut(BaseModel):
    id: int
    status: str
    description: Optional[str]
    client_username: str
    technicien_username: str
    organisation: str
    created_at: datetime
    updated_at: Optional[datetime]
    deleted_at: Optional[datetime]

    class Config:
        model_config = {
            'from_attributes': True,
            'extra': 'ignore'
        }

class PaginatedItem(BaseModel):
    total_result: int
    limit: int
    offset: int
    interventions: List[ItemOut]

class PatchItem(BaseModel):
    status: Optional[InterventionStatus] = None
    description: Optional[str] = None
