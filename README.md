# Case Study FastAPI - GarageOS 

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
make init-db-lite   # create a SQLite database file if you keep: DATABASE_URL=sqlite://...
make dev
````

## Context

This repository corresponds to a case study conducted during a technical interview for a **back-end developer** position at a startup.
This project allowed me to discover and learn new tools: **Alembic, Docker, PostgreSQL**.

The case study was provided with a pre-defined file structure.
I completed the entire project in just **2 days**, which allowed me to develop:
- Better stress and time management
- A sense of responsibility
- A strong work ethic
- High motivation
- Ability to adapt to the requirements

## Project Description
This project aims to design and implement a multi-organization REST API with a progress tracking mechanism (timeline).
The API is designed for repair shops. It manages several entities:

- Organizations: The repair shops themselves.
- Technicians: Staff attached to an organization.
- Clients: Managed by an organization.
- Interventions: Performed by technicians for clients.
- Timeline: A thread of events that tracks the progress of each intervention.

## Objectives
### Main Tasks
- Define the data schema, relationships, and relevant columns.
- Implement a REST API with secure routes.
- Handle headers and errors consistently.
- Write tests for key features.

## Expected Submissions
- A clear and executable README.md.
- A DESIGN.md explaining the design choices.
- Tests covering essential cases.
- Alembic migrations.

## Technical Details
- Language: Python ≥ 3.11
- Frameworks: FastAPI, SQLAlchemy 2.x, Alembic, Pydantic v2.
- Database: PostgreSQL.
- Security: Restrictive CORS, various security headers.
