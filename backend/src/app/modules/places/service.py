from app.core.errors import NotFoundError
from app.modules.places.models import Place
from app.modules.places.repository import PlaceRepository
from app.modules.places.schemas import (
    PlaceCard,
    PlaceDetail,
    PlaceReportCreate,
    PlaceReportOut,
    ReportReason,
)
from app.modules.tags.service import tags_to_out


class PlaceService:
    def __init__(self, repository: PlaceRepository) -> None:
        self._repository = repository

    async def list_cards_in_city(self, city_id: int) -> list[PlaceCard]:
        places = await self._repository.list_published_by_city(city_id)
        return [_to_card(place) for place in places]

    async def get_detail(self, place_id: int) -> PlaceDetail:
        place = await self._repository.get_published(place_id)
        if place is None:
            raise NotFoundError(f"Место #{place_id} не найдено")
        return _to_detail(place)

    async def report(self, place_id: int, data: PlaceReportCreate) -> PlaceReportOut:
        """Сохраняет жалобу пользователя на неактуальные данные места."""
        if not await self._repository.exists_published(place_id):
            raise NotFoundError(f"Место #{place_id} не найдено")
        report = await self._repository.add_report(place_id, data.reason.value, data.comment)
        return PlaceReportOut(
            id=report.id, place_id=report.place_id, reason=ReportReason(report.reason)
        )


def _to_card(place: Place) -> PlaceCard:
    return PlaceCard(
        id=place.id,
        name=place.name,
        summary=place.summary,
        address=place.address,
        price_level=place.price_level,
        is_indoor=place.is_indoor,
        cover_url=place.photos[0].url if place.photos else None,
        tags=tags_to_out(place.tags),
        is_promoted=place.is_promoted,
        verified_at=place.verified_at,
    )


def _to_detail(place: Place) -> PlaceDetail:
    return PlaceDetail(
        **_to_card(place).model_dump(),
        description=place.description,
        city_slug=place.city.slug,
        lat=place.lat,
        lng=place.lng,
        opening_hours=place.opening_hours,
        phone=place.phone,
        website_url=place.website_url,
        instagram_url=place.instagram_url,
        photos=[photo.url for photo in place.photos],
    )
