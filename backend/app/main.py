"""StormSight FastAPI application entry point.

PS 072 -- AIML-based Nowcasting of Thunderstorm and Lightning.
Adapted from PS 070 CycloneWatch architecture.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.session import dispose_engine

# -- Routers ---------------------------------------------------------------
from app.api.health import router as health_router
from app.api.ingest import router as ingest_router
from app.api.nowcast import router as nowcast_router
from app.api.alerts import router as alerts_router
from app.api.radar import router as radar_router
from app.api.lightning import router as lightning_router
from app.api.metrics import router as metrics_router
from app.api.replay import router as replay_router
from app.api.ws import router as ws_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage DB connection pool and background services lifecycle."""
    # -- Startup -----------------------------------------------------------
    # TODO: initialise Redis connection pool
    # TODO: start Kafka consumer tasks for radar/lightning streams
    yield
    # -- Shutdown ----------------------------------------------------------
    await dispose_engine()
    # TODO: close Redis pool
    # TODO: cancel Kafka consumer tasks


def create_app() -> FastAPI:
    app = FastAPI(
        title="StormSight API",
        description=(
            "AI/ML-based nowcasting of thunderstorms and lightning using "
            "multi-source atmospheric observations -- PS 072, SIH 2026."
        ),
        version=settings.api_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # -- CORS --------------------------------------------------------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -- Unified API v1 Surface --------------------------------------------
    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(health_router)
    api_v1.include_router(ingest_router)
    api_v1.include_router(nowcast_router)
    api_v1.include_router(alerts_router)
    api_v1.include_router(radar_router)
    api_v1.include_router(lightning_router)
    api_v1.include_router(metrics_router)
    api_v1.include_router(replay_router)
    app.include_router(api_v1)

    # -- Legacy Root Aliases -----------------------------------------------
    app.include_router(health_router)
    app.include_router(ingest_router)
    app.include_router(nowcast_router)
    app.include_router(alerts_router)
    app.include_router(radar_router)
    app.include_router(lightning_router)
    app.include_router(metrics_router)
    app.include_router(replay_router)
    app.include_router(ws_router)

    return app


app = create_app()
