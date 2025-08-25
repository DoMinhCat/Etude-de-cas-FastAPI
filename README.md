# Étude de cas FastAPI (GarageOS)

## Lancer rapidement
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make init-db-lite   # crée le fichier SQLite si vous gardez DATABASE_URL=sqlite://...
make dev