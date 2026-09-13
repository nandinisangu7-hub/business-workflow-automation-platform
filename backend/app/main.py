"""
Application entrypoint.

Phase 1 scope, deliberately: this file only wires up the FastAPI app,
CORS, and a health check. No domain routers are registered yet because no
domain exists yet (models arrive in Phase 2, auth in Phase 3, etc.).

From Phase 3 onward this file will grow one line per router, e.g.:
    app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
Route logic itself will never live in this file — see app/api/v1/*.py.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.auth import router as auth_router
from app.api.v1.requests import router as requests_router
from app.api.v1.workflow import router as workflow_router
from app.api.v1.audit import router as audit_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("workflow_platform")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("%s starting up in '%s' mode", settings.PROJECT_NAME, settings.ENVIRONMENT)
    yield
    logger.info("%s shutting down", settings.PROJECT_NAME)


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description=(
        "An enterprise-style workflow automation platform built to "
        "demonstrate full-stack application engineering practices."
    ),
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)
app.include_router(requests_router, prefix=settings.API_V1_PREFIX)
app.include_router(workflow_router, prefix=settings.API_V1_PREFIX)
app.include_router(audit_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["system"], summary="Liveness check")
def health_check() -> dict:
    """
    Used by Docker Compose / load balancers / CI to confirm the process is
    up. Deliberately does NOT touch the database — that will be a separate
    /health/db check once Phase 2 gives us something to query, so a DB
    outage and an app-process outage stay distinguishable.
    """
    return {"status": "ok", "service": settings.PROJECT_NAME, "environment": settings.ENVIRONMENT}
