from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import TimestampMixin

if TYPE_CHECKING:
    from app.modules.cities.models import City
    from app.modules.places.models import Place
    from app.modules.tags.models import Tag

scenario_tags = Table(
    "scenario_tags",
    Base.metadata,
    Column("scenario_id", ForeignKey("scenarios.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Scenario(TimestampMixin, Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), index=True)
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    duration_min: Mapped[int | None]
    is_published: Mapped[bool] = mapped_column(default=False)

    city: Mapped["City"] = relationship()
    tags: Mapped[list["Tag"]] = relationship(secondary=scenario_tags)
    steps: Mapped[list["ScenarioStep"]] = relationship(
        back_populates="scenario", order_by="ScenarioStep.position", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.title


class ScenarioStep(Base):
    __tablename__ = "scenario_steps"

    id: Mapped[int] = mapped_column(primary_key=True)
    scenario_id: Mapped[int] = mapped_column(
        ForeignKey("scenarios.id", ondelete="CASCADE"), index=True
    )
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(default=0)
    note: Mapped[str] = mapped_column(String(500), default="")

    scenario: Mapped[Scenario] = relationship(back_populates="steps")
    place: Mapped["Place"] = relationship()
