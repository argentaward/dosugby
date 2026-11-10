"""Репозиторий для идемпотентного сохранения импортированных мест в БД."""

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.modules.cities.models import City
from app.modules.ingestion.classifier import ClassifiedPlace
from app.modules.ingestion.clients import WikidataEnrichment
from app.modules.places.models import Place, PlacePhoto
from app.modules.tags.models import Tag, TagGroup


@dataclass(slots=True)
class UpsertCounters:
    created: int = 0
    updated: int = 0
    photos_added: int = 0


class IngestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_city_by_slug(self, slug: str) -> City | None:
        stmt = select(City).where(City.slug == slug)
        return await self._session.scalar(stmt)

    async def load_tag_map(self) -> dict[str, Tag]:
        """Возвращает словарь вида {'audience.family': Tag, 'vibe.active': Tag}."""
        stmt = select(Tag).options(selectinload(Tag.group)).join(TagGroup)
        tags = (await self._session.scalars(stmt)).all()
        return {f"{tag.group.code}.{tag.code}": tag for tag in tags}

    async def load_existing_places(self, city_id: int, external_source: str) -> dict[str, Place]:
        stmt = (
            select(Place)
            .where(Place.city_id == city_id, Place.external_source == external_source)
            .options(selectinload(Place.tags), selectinload(Place.photos))
        )
        places = (await self._session.scalars(stmt)).all()
        return {p.external_id: p for p in places if p.external_id is not None}

    async def upsert_places(
        self,
        city: City,
        items: list[ClassifiedPlace],
        enrichments: dict[str, WikidataEnrichment],
    ) -> UpsertCounters:
        tag_map = await self.load_tag_map()
        existing_by_ext_id = await self.load_existing_places(city.id, "osm")
        counters = UpsertCounters()
        now = datetime.now(UTC).replace(tzinfo=None)

        for item in items:
            enrichment = enrichments.get(item.wikidata_id or "")
            photo_url = item.commons_image_url or (
                enrichment.image_url if enrichment is not None else None
            )
            description = enrichment.description if enrichment and enrichment.description else ""
            matched_tags = [tag_map[k] for k in sorted(item.tag_keys) if k in tag_map]

            existing = existing_by_ext_id.get(item.external_id)
            if existing is None:
                place = _build_new_place(city.id, item, description, matched_tags, now)
                if photo_url:
                    place.photos.append(PlacePhoto(url=photo_url, sort_order=0))
                    counters.photos_added += 1
                self._session.add(place)
                existing_by_ext_id[item.external_id] = place
                counters.created += 1
            else:
                _update_existing_place(existing, item, description, matched_tags, now)
                if photo_url and not existing.photos:
                    existing.photos.append(PlacePhoto(url=photo_url, sort_order=0))
                    counters.photos_added += 1
                counters.updated += 1

        await self._session.commit()
        return counters


def _build_new_place(
    city_id: int,
    item: ClassifiedPlace,
    description: str,
    tags: list[Tag],
    verified_at: datetime,
) -> Place:
    return Place(
        city_id=city_id,
        external_source=item.external_source,
        external_id=item.external_id,
        wikidata_id=item.wikidata_id,
        name=item.name,
        summary=item.summary,
        description=description,
        address=item.address,
        lat=item.lat,
        lng=item.lng,
        price_level=item.price_level,
        is_indoor=item.is_indoor,
        opening_hours=item.opening_hours,
        phone=item.phone,
        website_url=item.website_url,
        instagram_url=item.instagram_url,
        is_published=True,
        verified_at=verified_at,
        tags=tags,
    )


def _update_existing_place(
    place: Place,
    item: ClassifiedPlace,
    description: str,
    tags: list[Tag],
    verified_at: datetime,
) -> None:
    place.name = item.name
    place.summary = item.summary
    if description and not place.description:
        place.description = description
    place.address = item.address
    place.lat = item.lat
    place.lng = item.lng
    place.opening_hours = item.opening_hours
    place.phone = item.phone
    place.website_url = item.website_url
    place.instagram_url = item.instagram_url
    place.wikidata_id = item.wikidata_id
    place.verified_at = verified_at
    if not place.tags:
        place.tags = tags
