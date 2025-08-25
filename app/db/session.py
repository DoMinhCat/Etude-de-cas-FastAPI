from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def _make_engine(url: str):
    # SQLite fichier nécessite 'check_same_thread=False'
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(url, pool_pre_ping=True, future=True, connect_args=connect_args)

engine = _make_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    """Dépendance FastAPI pour une session DB.
    TODO: utilisez-la dans vos routes une fois la persistance implémentée.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
