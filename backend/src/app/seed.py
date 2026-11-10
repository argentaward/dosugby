"""Тестовые данные для локальной разработки.

Запуск: `uv run python -m app.seed`. Повторный запуск ничего не дублирует.

ВНИМАНИЕ: адреса и описания — демонстрационные и требуют проверки перед публикацией
(поэтому verified_at не заполнен).
"""

import asyncio
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import engine, session_factory
from app.models_registry import City, Place, Scenario, ScenarioStep, Tag, TagGroup

TAG_GROUPS: dict[str, tuple[str, list[tuple[str, str, str]]]] = {
    "audience": (
        "С кем вы?",
        [
            ("family", "С семьёй", "👨‍👩‍👧"),
            ("couple", "Вдвоём", "💑"),
            ("friends", "С друзьями", "🎉"),
            ("solo", "Один", "🧘"),
        ],
    ),
    "vibe": (
        "Какой вайб?",
        [
            ("active", "Активный", "🏃"),
            ("calm", "Спокойный", "🌿"),
            ("culture", "Культурный", "🏛"),
            ("food", "Вкусный", "🍕"),
        ],
    ),
}


@dataclass(frozen=True)
class _PlaceSeed:
    name: str
    summary: str
    address: str
    price_level: int
    is_indoor: bool | None
    tags: tuple[str, ...]  # "group.code"


PLACES = [
    _PlaceSeed(
        "Лесопарк «Пышки»",
        "Тропы вдоль Немана, велодорожки и смотровые площадки",
        "Гродно, лесопарк Пышки",
        0,
        False,
        ("audience.family", "audience.friends", "audience.solo", "vibe.active", "vibe.calm"),
    ),
    _PlaceSeed(
        "Парк Жилибера",
        "Старейший ботанический сад в центре города",
        "Гродно, ул. Ожешко",
        0,
        False,
        ("audience.family", "audience.couple", "audience.solo", "vibe.calm"),
    ),
    _PlaceSeed(
        "Гродненский зоопарк",
        "Один из старейших зоопарков Беларуси",
        "Гродно, ул. Тимирязева, 11",
        1,
        None,
        ("audience.family", "vibe.active"),
    ),
    _PlaceSeed(
        "Старый замок",
        "Историко-археологический музей на берегу Немана",
        "Гродно, ул. Замковая, 22",
        1,
        True,
        ("audience.family", "audience.couple", "audience.solo", "vibe.culture"),
    ),
    _PlaceSeed(
        "Коложская церковь",
        "Памятник XII века с видом на Неман",
        "Гродно, ул. Коложская, 6",
        0,
        None,
        ("audience.couple", "audience.solo", "vibe.culture", "vibe.calm"),
    ),
]


def _seed_tags(session: AsyncSession) -> dict[str, Tag]:
    tags: dict[str, Tag] = {}
    for order, (group_code, (title, options)) in enumerate(TAG_GROUPS.items()):
        group_tags = [
            Tag(code=code, title=tag_title, icon=icon, sort_order=tag_order)
            for tag_order, (code, tag_title, icon) in enumerate(options)
        ]
        session.add(TagGroup(code=group_code, title=title, sort_order=order, tags=group_tags))
        tags.update({f"{group_code}.{tag.code}": tag for tag in group_tags})
    return tags


async def seed(session: AsyncSession) -> bool:
    """Наполняет пустую базу. Возвращает False, если данные уже есть."""
    if await session.scalar(select(City.id).where(City.slug == "grodno")):
        return False

    city = City(slug="grodno", name="Гродно", lat=53.6779, lng=23.8297)
    tags = _seed_tags(session)
    places = [
        Place(
            city=city,
            name=p.name,
            summary=p.summary,
            address=p.address,
            price_level=p.price_level,
            is_indoor=p.is_indoor,
            is_published=True,
            tags=[tags[key] for key in p.tags],
        )
        for p in PLACES
    ]
    scenario = Scenario(
        city=city,
        title="Исторический Гродно за полдня",
        description="Прогулка от Старого замка к Коложе с видами на Неман",
        duration_min=180,
        is_published=True,
        tags=[tags["audience.couple"], tags["audience.solo"], tags["vibe.culture"]],
        steps=[
            ScenarioStep(place=places[3], position=1, note="Начните с музея в замке"),
            ScenarioStep(place=places[4], position=2, note="Пройдите вдоль Немана к Коложе"),
        ],
    )
    session.add_all([city, *places, scenario])
    await session.commit()
    return True


async def _main() -> None:
    async with session_factory() as session:
        created = await seed(session)
    await engine.dispose()
    print("Тестовые данные добавлены" if created else "Данные уже есть — пропускаю")


if __name__ == "__main__":
    asyncio.run(_main())
