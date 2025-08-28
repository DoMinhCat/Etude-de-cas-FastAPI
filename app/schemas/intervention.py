from pydantic import BaseModel
from datetime import datetime, timezone
from typing import Optional
import enum

class InterventionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# class CreateItem(BaseModel):
#     status = 
#     description= = Optional[str]
#     created_at = 
#     update