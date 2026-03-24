"""Coordinaut FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db.engine import engine, SessionLocal
from app.models.base import Base
from app.services.resource_service import seed_default_resource

from app.api import sessions, leases, queue, messages, tickets, resources, events, config, launcher, repos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Seed default resource
    db = SessionLocal()
    try:
        seed_default_resource(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title="Coordinaut",
    description="Local-first coordination layer for autonomous coding workflows",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(sessions.router)
app.include_router(leases.router)
app.include_router(queue.router)
app.include_router(messages.router)
app.include_router(tickets.router)
app.include_router(resources.router)
app.include_router(events.router)
app.include_router(config.router)
app.include_router(launcher.router)
app.include_router(repos.router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}
