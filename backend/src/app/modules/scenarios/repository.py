from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.scenarios.models import Scenario, ScenarioStep
from app.modules.tags.models import Tag


class ScenarioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_published_by_city(self, city_id: int) -> Sequence[Scenario]:
        stmt = (
            select(Scenario)
            .where(Scenario.city_id == city_id, Scenario.is_published.is_(True))
            .options(
                selectinload(Scenario.tags).selectinload(Tag.group),
                selectinload(Scenario.steps).selectinload(ScenarioStep.place),
            )
        )
        return (await self._session.scalars(stmt)).all()
