from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.modules.tags.schemas import TagOut


class PlaceCard(BaseModel):
    """Короткая карточка места для списков и результатов подбора."""

    id: int
    name: str
    summary: str
    address: str
    price_level: int
    is_indoor: bool | None
    cover_url: str | None
    tags: list[TagOut]
    is_promoted: bool
    verified_at: datetime | None


class PlaceDetail(PlaceCard):
    description: str
    city_slug: str
    lat: float | None
    lng: float | None
    opening_hours: str | None
    phone: str | None
    website_url: str | None
    instagram_url: str | None
    photos: list[str]


class ReportReason(StrEnum):
    CLOSED = "closed"
    WRONG_HOURS = "wrong_hours"
    WRONG_PRICE = "wrong_price"
    WRONG_ADDRESS = "wrong_address"
    OTHER = "other"


class PlaceReportCreate(BaseModel):
    reason: ReportReason
    comment: str = Field(default="", max_length=1000)


class PlaceReportOut(BaseModel):
    id: int
    place_id: int
    reason: ReportReason
