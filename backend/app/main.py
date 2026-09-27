import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import citizens, benefits, applications, documents
from .api import schemes, scheme_versions, scheme_sources, scheme_admin
from .api import auth, deployment
from .api.error_handlers import register_exception_handlers
# Ensure new models are imported so Alembic/SQLAlchemy picks them up
from app.models import scheme_audit  # noqa: F401

app = FastAPI(title="JanSetu API", version="0.1.0")
register_exception_handlers(app)

default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

env_origins = os.environ.get("CORS_ORIGINS", "")
if env_origins:
    for o in env_origins.split(","):
        cleaned = o.strip()
        if cleaned and cleaned not in default_origins:
            default_origins.append(cleaned)

app.add_middleware(
    CORSMiddleware,
    allow_origins=default_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(citizens.router, prefix="/api/citizens", tags=["Citizens"])
app.include_router(benefits.router, prefix="/api/benefits", tags=["Benefits"])
app.include_router(applications.router, prefix="/api/applications", tags=["Applications"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
# Also support root /auth prefix for direct Google OAuth callbacks
app.include_router(auth.router, prefix="/auth", tags=["Authentication (Root Alias)"])
app.include_router(deployment.router, prefix="/api/deployment", tags=["Deployment Readiness"])

from app.api.endpoints import agent
app.include_router(agent.router, prefix="/api/agent", tags=["Agent"])

# Phase 5B — Scheme Intelligence APIs
app.include_router(schemes.router, prefix="/api/schemes", tags=["Schemes"])
app.include_router(scheme_versions.router, prefix="/api/scheme-versions", tags=["Scheme Versions"])
app.include_router(scheme_sources.router, prefix="/api/scheme-sources", tags=["Scheme Sources"])
app.include_router(scheme_admin.router, prefix="/api/scheme-versions", tags=["Scheme Admin"])
# Review endpoints are under /api/scheme-review
from app.api import scheme_admin as scheme_review_router
app.include_router(scheme_review_router.router, prefix="/api/scheme-review", tags=["Scheme Review"])

@app.get("/")
def root():
    return {
        "app": "JanSetu API",
        "status": "online",
        "version": "0.1.0",
        "documentation": "/docs",
        "health": "/api/health",
        "readiness": "/api/deployment/readiness",
    }

@app.get("/api/health")
def health_check():
    return {"status": "ok"}
