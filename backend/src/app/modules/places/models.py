from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.core.models import TimestampMixin

if TYPE_CHECKING:
    from app.modules.cities.models import City
    from app.modules.tags.models import Tag

place_tags = Table(
    "place_tags",
    Base.metadata,
    Column("place_id", ForeignKey("places.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Place(TimestampMixin, Base):
    __tablename__ = "places"
    __table_args__ = (UniqueConstraint("external_source", "external_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int] = mapped_column(ForeignKey("cities.id", ondelete="RESTRICT"), index=True)
    external_source: Mapped[str | None] = mapped_column(String(32))
    external_id: Mapped[str | None] = mapped_column(String(128))
    wikidata_id: Mapped[str | None] = mapped_column(String(32))
    name: Mapped[str] = mapped_column(String(200))
    summary: Mapped[str] = mapped_column(String(300), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    address: Mapped[str] = mapped_column(String(300), default="")
    lat: Mapped[float | None]
    lng: Mapped[float | None]
    # 0 — бесплатно, 1 — эконом, 2 — средний, 3 — комфорт
    price_level: Mapped[int] = mapped_column(SmallInteger, default=0)
    # True — под крышей, False — на улице, None — и то, и другое
    is_indoor: Mapped[bool | None]
    opening_hours: Mapped[str | None] = mapped_column(String(300))
    phone: Mapped[str | None] = mapped_column(String(32))
    website_url: Mapped[str | None] = mapped_column(String(500))
    instagram_url: Mapped[str | None] = mapped_column(String(500))
    is_published: Mapped[bool] = mapped_column(default=False)
    is_promoted: Mapped[bool] = mapped_column(default=False)
    # Когда данные последний раз проверялись вручную
    verified_at: Mapped[datetime | None] = mapped_column(DateTime)

    city: Mapped["City"] = relationship()
    tags: Mapped[list["Tag"]] = relationship(secondary=place_tags)
    photos: Mapped[list["PlacePhoto"]] = relationship(
        back_populates="place", order_by="PlacePhoto.sort_order", cascade="all, delete-orphan"
    )

    def __str__(self) -> str:
        return self.name


class PlacePhoto(Base):
    __tablename__ = "place_photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), index=True)
    url: Mapped[str] = mapped_column(String(500))
    sort_order: Mapped[int] = mapped_column(default=0)

    place: Mapped[Place] = relationship(back_populates="photos")


class PlaceReport(Base):
    """Сообщение пользователя о неактуальных данных («закрыто», «другие цены» и т.п.)."""

    __tablename__ = "place_reports"

    id: Mapped[int] = mapped_column(primary_key=True)
    place_id: Mapped[int] = mapped_column(ForeignKey("places.id", ondelete="CASCADE"), index=True)
    reason: Mapped[str] = mapped_column(String(32))
    comment: Mapped[str] = mapped_column(String(1000), default="")
    is_resolved: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    place: Mapped[Place] = relationship()
