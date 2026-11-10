"""Импорт всех ORM-моделей в одном месте.

Нужен, чтобы SQLAlchemy знал обо всех связях, а Alembic видел полную схему.
Добавили новый models.py — добавьте импорт сюда.
"""

from app.core.db import Base
from app.modules.cities.models import City
from app.modules.places.models import Place, PlacePhoto, PlaceReport
from app.modules.scenarios.models import Scenario, ScenarioStep
from app.modules.tags.models import Tag, TagGroup

__all__ = [
    "Base",
    "City",
    "Place",
    "PlacePhoto",
    "PlaceReport",
    "Scenario",
    "ScenarioStep",
    "Tag",
    "TagGroup",
]
