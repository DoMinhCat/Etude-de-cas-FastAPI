from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

class ClientOut(BaseModel):
    id: int
    first_name: str
    last_name: str
    username: str
    email: EmailStr
    phone: Optional[str]
    created_at: datetime
    deleted_at: Optional[datetime]

    class Config:
        model_config = {
            'from_attributes': True,
            'extra': 'ignore'
        }

class PaginatedClient(BaseModel):
    total_result: int
    limit: int
    offset: int
    clients: List[ClientOut]

class CreateClient(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str
    email: EmailStr
    phone: Optional[str]

class PatchClient(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    username: Optional[str]
    email: Optional[EmailStr]
    phone: Optional[str]
