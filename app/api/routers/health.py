from fastapi import APIRouter

router = APIRouter(tags=["health"])

@router.get("/health")
def health():
    """Ping simple, doit répondre immédiatement."""
    return {"status": "ok"}
