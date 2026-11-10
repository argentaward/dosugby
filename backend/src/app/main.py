from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models_registry  # noqa: F401  — регистрирует все модели до старта
from app.admin import setup_admin
from app.core.config import get_settings
from app.core.db import engine
from app.core.errors import register_error_handlers
from app.modules.cities.router import router as cities_router
from app.modules.places.router import router as places_router
from app.modules.recommendations.router import router as recommendations_router
from app.modules.tags.router import router as tags_router

API_PREFIX = "/api/v1"


@asynccontextmanager
async def _lifespan(_: FastAPI) -> AsyncIterator[None]:
    yield
    await engine.dispose()


def _build_api_router() -> APIRouter:
    api = APIRouter(prefix=API_PREFIX)

    @api.get("/health", tags=["system"], summary="Проверка работоспособности")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    for router in (cities_router, tags_router, places_router, recommendations_router):
        api.include_router(router)
    return api


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Dosug API", version="0.1.0", lifespan=_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_error_handlers(app)
    app.include_router(_build_api_router())
    setup_admin(app, engine, settings)
    return app


app = create_app()
