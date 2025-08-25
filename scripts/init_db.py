"""
Init DB helper:
- Pour SQLite: crée le fichier ./garageos.db si absent en ouvrant une connexion.
- Pour PostgreSQL: no-op utile (la connexion réussira si Postgres est dispo).
"""
from sqlalchemy import text
from app.db.session import engine

def main():
    with engine.begin() as conn:
        conn.execute(text("SELECT 1"))
    print(f"[init-db-lite] DB prête: {engine.url}")

if __name__ == "__main__":
    main()