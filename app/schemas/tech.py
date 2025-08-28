from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class TechOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    organisation: str
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        model_config = {
            'from_attributes': True,
            'extra': 'ignore'
        }

class PaginatedTech(BaseModel):
    total_result: int
    limit: int
    offset: int
    techniciens: List[TechOut]

class CreateTech(BaseModel):
    name: str
    email: EmailStr

class PatchTech(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
