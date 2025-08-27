from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import SecurityHeadersMiddleware
from app.api.routers import health, clients, technicians, interventions, events, auth

app = FastAPI(title=settings.APP_NAME)

# Security headers & CORS
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(health.router)
app.include_router(clients.router)
app.include_router(technicians.router)
app.include_router(interventions.router)
app.include_router(events.router)