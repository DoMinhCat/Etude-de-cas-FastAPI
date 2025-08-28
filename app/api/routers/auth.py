from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.client import Client
from app.db.session import get_db
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["auth"], include_in_schema=False)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    result = db.execute(select(Client).filter(func.lower(Client.username) == form_data.username.lower()))
    user = result.scalars().first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Identifiants invalides.")

    if user.deleted_at is not None:
        raise HTTPException(status_code=401, detail="Client déjà supprimé.")
    
    token_data = {"sub": user.username, "org_id": user.org_id}
    token = create_access_token(token_data)
    return {"access_token": token, "token_type": "bearer"}
