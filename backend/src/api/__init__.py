"""
API package for traffic simulation platform.
Contains all FastAPI routes and endpoints.
"""

from fastapi import FastAPI
from .personas import router as personas_router
from .campaigns import router as campaigns_router
from .sessions import router as sessions_router
from .analytics import router as analytics_router
from .campaign_metrics import router as campaign_metrics_router
from ..websockets.campaign_updates import router as ws_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Traffic Simulation Platform API",
        description="API for managing traffic simulation campaigns and analytics",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Include routers
    app.include_router(personas_router, prefix="/api/v1")
    app.include_router(campaigns_router, prefix="/api/v1")
    app.include_router(sessions_router, prefix="/api/v1")
    app.include_router(analytics_router, prefix="/api/v1")
    app.include_router(campaign_metrics_router, prefix="/api/v1")
    # WebSocket routes (no API prefix)
    app.include_router(ws_router)
    
    return app
