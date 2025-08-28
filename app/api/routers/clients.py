from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_
from datetime import datetime, timezone

from app.api.deps import get_db, get_current_user
from app.models.client import Client
from app.schemas.client import PaginatedClient, ClientOut, CreateClient, PatchClient
from app.core.security import hash_password

router = APIRouter(prefix="/clients", tags=["clients"])

default_limit = 50
max_limit = 200

@router.post("", status_code=status.HTTP_201_CREATED)
def create_client(
    new_user: CreateClient,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Créer un client (org courante).
    TODO: définir schémas Pydantic, insérer en base (filtré org), gérer validations & erreurs.
    """

    query = select(Client).filter(Client.org_id == current_user.org_id)

    check_query = query.filter(func.lower(Client.username) == new_user.username.lower())
    db_user = db.execute(check_query).scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Cet username est déjà inscrit. Veuillez choisir un autre username.")
    
    check_query = query.filter(func.lower(Client.email) == new_user.email.lower())
    db_user = db.execute(check_query).scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Cette adresse email est déjà inscrite. Veuillez choisir une autre adresse.")
    
    check_query = query.filter(func.lower(Client.phone) == new_user.phone)
    db_user = db.execute(check_query).scalars().first()
    if db_user:
        raise HTTPException(status_code=400, detail="Ce numéro de téléphone est déjà inscrit. Veuillez choisir un autre numéro.")
    
    hashed_password = hash_password(new_user.password)
    user_to_add = Client(first_name=new_user.first_name, last_name=new_user.last_name, username=new_user.username, hashed_password=hashed_password, email=new_user.email, phone=new_user.phone, org_id=current_user.org_id)
    
    try:
        db.add(user_to_add)
        db.commit()
        db.refresh(user_to_add)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur imprévue lors de la création du client."
        )
    return {"message": f"Nouveau client '{new_user.username}' créé avec succès."}

@router.get("", status_code=status.HTTP_200_OK, response_model=PaginatedClient)
def list_clients(
    q: str | None = None,
    limit: int = default_limit,
    offset: int = 0,
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lister clients de l'org (pagination & filtre q).
    TODO: requête SQL (limit/offset), recherche q (au choix: name/email), retour liste (+ total si voulu).
    """

    if limit < 1 or limit > max_limit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Limit doit être entre 1 et {max_limit}.")
    if offset < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Offset ne peut pas être négatif.")
    
    query = select(Client).filter(Client.org_id == current_user.org_id)

    # Filtre
    if q:
        search = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Client.first_name).like(search),
                func.lower(Client.last_name).like(search),
                func.lower(Client.email).like(search)
            )
        )
    # Total number of results before offset or limit
    total = db.execute(select(func.count()).select_from(query.subquery())).scalar()
    query = query.limit(limit).offset(offset)

    try:
        clients = db.execute(query).scalars().all()
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erreur serveur imprévue.")
    
    if not clients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Aucun client trouvé pour votre organisation.")
    
    return PaginatedClient(
        total_result=total,
        limit=limit,
        offset=offset,
        clients=[ClientOut.model_validate(c, from_attributes=True) for c in clients]
    )

@router.get("/{client_id}", status_code=status.HTTP_200_OK, response_model=ClientOut)
def get_client(
    client_id: int, 
    current_user: Client = Depends(get_current_user),
    db: Session = Depends(get_db)
    ):
    """Récupérer un client (filtré org).
    TODO: SELECT + 404 si introuvable/hors org.
    """
    
    query = select(Client).filter(current_user.org_id == Client.org_id, client_id == Client.id)
    client = db.execute(query).scalar_one_or_none()

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client avec id {client_id} introuvable dans votre organisation.")
    
    return client

@router.patch("/{client_id}", status_code=status.HTTP_200_OK, response_model=ClientOut)
def update_client(
    client_id: int, 
    patch_data: PatchClient,
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user)
    ):
    """PATCH partiel client.
    TODO: schéma PATCH, appliquer champs présents, validations.
    NOTE: all provided fields must be filled in with their original values if no change is wanted
    """
    
    client = db.execute(
        select(Client).filter(Client.id == client_id, Client.org_id == current_user.org_id)
    ).scalars().first()

    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Client avec id {client_id} introuvable dans votre organisation.")
    
    if client.deleted_at is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Client avec id {client_id} est déjà supprimé.")

    if patch_data.username and patch_data.username.lower() != client.username.lower():
        exists = db.execute(
            select(Client).filter(
                Client.org_id == current_user.org_id,
                func.lower(Client.username) == patch_data.username.lower()
            )
        ).scalars().first()
        if exists:
            raise HTTPException(status_code=409, detail="Cet username est déjà inscrit.")

    if patch_data.email and patch_data.email.lower() != client.email.lower():
        exists = db.execute(
            select(Client).filter(
                Client.org_id == current_user.org_id,
                func.lower(Client.email) == patch_data.email.lower()
            )
        ).scalars().first()
        if exists:
            raise HTTPException(status_code=409, detail="Cette adresse email est déjà inscrite.")

    if patch_data.phone and patch_data.phone != client.phone:
        exists = db.execute(
            select(Client).filter(
                Client.org_id == current_user.org_id,
                Client.phone == patch_data.phone
            )
        ).scalars().first()
        if exists:
            raise HTTPException(status_code=409, detail="Ce numéro de téléphone est déjà utilisé.")

    for field, value in patch_data.model_dump(exclude_unset=True).items():
        setattr(client, field, value)

    try:
        db.commit()
        db.refresh(client)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur imprévue lors de la mise à jour du client."
        )
    
    return ClientOut.model_validate(client, from_attributes=True)

@router.delete("/{client_id}", status_code=status.HTTP_200_OK)
def delete_client(
    client_id: int, 
    db: Session = Depends(get_db),
    current_user: Client = Depends(get_current_user)
    ):
    """Supprimer client.
    TODO: soft-delete (deleted_at) recommandé OU hard delete (documentez), vérifier appartenance org.
    """
    
    client = db.execute(
        select(Client).filter(Client.id == client_id, Client.org_id == current_user.org_id)
    ).scalars().first()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client avec id {client_id} introuvable dans votre organisation."
        )
    
    if client.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Client déjà supprimé."
        )
    
    client.deleted_at = datetime.now(timezone.utc)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur serveur imprévue lors de la suppression du client."
        )

    return {"message" : "Client supprimé avec succès."}
