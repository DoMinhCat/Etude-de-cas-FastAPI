from pydantic import BaseModel, EmailStr
from typing import List

class TechOut(BaseModel):
    name: str
    email: EmailStr
    org_id: int

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