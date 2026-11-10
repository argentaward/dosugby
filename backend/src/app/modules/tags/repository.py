from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.tags.models import TagGroup


class TagRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_groups_with_tags(self) -> Sequence[TagGroup]:
        stmt = select(TagGroup).options(selectinload(TagGroup.tags)).order_by(TagGroup.sort_order)
        return (await self._session.scalars(stmt)).all()
