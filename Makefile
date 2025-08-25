.PHONY: dev init-db revise test init-db-lite

dev:
	python -m uvicorn app.main:app --reload

# Crée une révision Alembic auto (après avoir défini vos modèles)
revise:
	alembic revision --autogenerate -m "auto"

# Applique les migrations
init-db:
	alembic upgrade head

# Initialise la DB (crée le fichier SQLite s'il n'existe pas) sans migrations
init-db-lite:
	python -m scripts.init_db

# Tests
test:
	pytest -q
