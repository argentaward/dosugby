from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.cities.models import City


class CityRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_active(self) -> Sequence[City]:
        stmt = select(City).where(City.is_active.is_(True)).order_by(City.name)
        return (await self._session.scalars(stmt)).all()

    async def get_active_by_slug(self, slug: str) -> City | None:
        stmt = select(City).where(City.slug == slug, City.is_active.is_(True))
        return await self._session.scalar(stmt)
