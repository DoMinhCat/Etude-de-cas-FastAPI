from pydantic import BaseModel, EmailStr

class TechOut(BaseModel):
    name: str
    email: EmailStr
    organisation: str

class CreateTech(BaseModel):
    name: str
    email: EmailStr