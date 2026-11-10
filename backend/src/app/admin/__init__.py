"""Веб-админка для наполнения базы (sqladmin) — доступна по /admin."""

import secrets

from fastapi import FastAPI, Request
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.models_registry import (
    City,
    Place,
    PlacePhoto,
    PlaceReport,
    Scenario,
    ScenarioStep,
    Tag,
    TagGroup,
)


class _AdminAuth(AuthenticationBackend):
    def __init__(self, settings: Settings) -> None:
        super().__init__(secret_key=settings.secret_key)
        self._username = settings.admin_username
        self._password = settings.admin_password

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))
        is_valid = secrets.compare_digest(username, self._username) and secrets.compare_digest(
            password, self._password
        )
        if is_valid:
            request.session.update({"admin": True})
        return is_valid

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        return bool(request.session.get("admin"))


class CityAdmin(ModelView, model=City):
    name, name_plural, icon = "Город", "Города", "fa-solid fa-city"
    column_list = [City.id, City.name, City.slug, City.is_active]


class TagGroupAdmin(ModelView, model=TagGroup):
    name, name_plural, icon = "Группа тегов", "Группы тегов", "fa-solid fa-layer-group"
    column_list = [TagGroup.id, TagGroup.title, TagGroup.code, TagGroup.sort_order]


class TagAdmin(ModelView, model=Tag):
    name, name_plural, icon = "Тег", "Теги", "fa-solid fa-tag"
    column_list = [Tag.id, Tag.icon, Tag.title, Tag.code, Tag.group]


class PlaceAdmin(ModelView, model=Place):
    name, name_plural, icon = "Место", "Места", "fa-solid fa-location-dot"
    column_list = [
        Place.id,
        Place.name,
        Place.city,
        Place.external_source,
        Place.price_level,
        Place.is_published,
        Place.is_promoted,
        Place.verified_at,
    ]
    column_searchable_list = [Place.name, Place.address]
    column_sortable_list = [Place.id, Place.name, Place.verified_at]
    form_excluded_columns = [Place.created_at, Place.updated_at]


class PlacePhotoAdmin(ModelView, model=PlacePhoto):
    name, name_plural, icon = "Фото", "Фото мест", "fa-solid fa-image"
    column_list = [PlacePhoto.id, PlacePhoto.place, PlacePhoto.url, PlacePhoto.sort_order]


class PlaceReportAdmin(ModelView, model=PlaceReport):
    name, name_plural, icon = "Жалоба", "Жалобы", "fa-solid fa-flag"
    column_list = [
        PlaceReport.id,
        PlaceReport.place,
        PlaceReport.reason,
        PlaceReport.is_resolved,
        PlaceReport.created_at,
    ]
    can_create = False


class ScenarioAdmin(ModelView, model=Scenario):
    name, name_plural, icon = "Сценарий", "Сценарии", "fa-solid fa-route"
    column_list = [Scenario.id, Scenario.title, Scenario.city, Scenario.is_published]
    form_excluded_columns = [Scenario.created_at, Scenario.updated_at]


class ScenarioStepAdmin(ModelView, model=ScenarioStep):
    name, name_plural, icon = "Шаг сценария", "Шаги сценариев", "fa-solid fa-shoe-prints"
    column_list = [
        ScenarioStep.id,
        ScenarioStep.scenario,
        ScenarioStep.position,
        ScenarioStep.place,
    ]


_VIEWS = (
    CityAdmin,
    TagGroupAdmin,
    TagAdmin,
    PlaceAdmin,
    PlacePhotoAdmin,
    PlaceReportAdmin,
    ScenarioAdmin,
    ScenarioStepAdmin,
)


def setup_admin(app: FastAPI, engine: AsyncEngine, settings: Settings) -> None:
    admin = Admin(
        app,
        engine,
        title="Dosug — админка",
        authentication_backend=_AdminAuth(settings),
    )
    for view in _VIEWS:
        admin.add_view(view)
