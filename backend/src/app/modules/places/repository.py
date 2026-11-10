from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.places.models import Place, PlaceReport
from app.modules.tags.models import Tag

# Связанные данные, нужные для построения карточек (иначе — ленивые запросы, которых нет в async).
_CARD_OPTIONS = (
    selectinload(Place.tags).selectinload(Tag.group),
    selectinload(Place.photos),
)


class PlaceRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_published_by_city(self, city_id: int) -> Sequence[Place]:
        stmt = (
            select(Place)
            .where(Place.city_id == city_id, Place.is_published.is_(True))
            .options(*_CARD_OPTIONS)
        )
        return (await self._session.scalars(stmt)).all()

    async def get_published(self, place_id: int) -> Place | None:
        stmt = (
            select(Place)
            .where(Place.id == place_id, Place.is_published.is_(True))
            .options(*_CARD_OPTIONS, selectinload(Place.city))
        )
        return await self._session.scalar(stmt)

    async def exists_published(self, place_id: int) -> bool:
        stmt = select(Place.id).where(Place.id == place_id, Place.is_published.is_(True))
        return (await self._session.scalar(stmt)) is not None

    async def add_report(self, place_id: int, reason: str, comment: str) -> PlaceReport:
        report = PlaceReport(place_id=place_id, reason=reason, comment=comment)
        self._session.add(report)
        await self._session.commit()
        await self._session.refresh(report)
        return report
