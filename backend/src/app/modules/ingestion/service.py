"""Сервис автоматического сбора мест из OpenStreetMap + Wikidata."""

from dataclasses import dataclass

from app.core.errors import NotFoundError
from app.modules.ingestion.classifier import (
    ClassifiedPlace,
    RawOsmElement,
    classify_osm_element,
)
from app.modules.ingestion.clients import OverpassClient, WikidataClient
from app.modules.ingestion.repository import IngestionRepository


@dataclass(frozen=True, slots=True)
class IngestionStats:
    city_slug: str
    fetched_raw: int
    classified: int
    created: int
    updated: int
    photos_added: int


class IngestionService:
    def __init__(
        self,
        repository: IngestionRepository,
        overpass: OverpassClient,
        wikidata: WikidataClient,
    ) -> None:
        self._repository = repository
        self._overpass = overpass
        self._wikidata = wikidata

    async def ingest_city(self, city_slug: str, radius_m: int = 10_000) -> IngestionStats:
        """Загружает, классифицирует и сохраняет места досуга для указанного города."""
        city = await self._repository.get_city_by_slug(city_slug)
        if city is None:
            raise NotFoundError(f"Город '{city_slug}' не найден в БД")

        raw_elements = await self._overpass.fetch_elements(city.lat, city.lng, radius_m)
        classified = _classify_and_deduplicate(raw_elements)

        wikidata_ids = [item.wikidata_id for item in classified if item.wikidata_id is not None]
        enrichments = await self._wikidata.fetch_enrichment(wikidata_ids)

        counters = await self._repository.upsert_places(city, classified, enrichments)
        return IngestionStats(
            city_slug=city.slug,
            fetched_raw=len(raw_elements),
            classified=len(classified),
            created=counters.created,
            updated=counters.updated,
            photos_added=counters.photos_added,
        )


def _classify_and_deduplicate(
    raw_elements: list[RawOsmElement],
) -> list[ClassifiedPlace]:
    by_ext_id: dict[str, ClassifiedPlace] = {}
    for elem in raw_elements:
        item = classify_osm_element(elem)
        if item is not None:
            by_ext_id[item.external_id] = item
    return list(by_ext_id.values())
