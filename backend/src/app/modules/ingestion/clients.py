"""HTTP-клиенты для Overpass API (OpenStreetMap) и Wikidata API."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final

import httpx

from app.modules.ingestion.classifier import RawOsmElement, commons_to_image_url

OVERPASS_ENDPOINTS: Final[tuple[str, ...]] = (
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
)
WIKIDATA_API_URL: Final = "https://www.wikidata.org/w/api.php"
USER_AGENT: Final = "DosugBelarusApp/0.1 (https://github.com/whitecow/dosug)"


@dataclass(frozen=True, slots=True)
class WikidataEnrichment:
    description: str | None
    image_url: str | None


def build_overpass_query(lat: float, lng: float, radius_m: int) -> str:
    """Формирует запрос Overpass QL для сбора мест отдыха вокруг координат города."""
    around = f"(around:{radius_m},{lat},{lng})"
    return f"""
[out:json][timeout:45];
(
  nwr["historic"="castle"]{around};
  nwr["tourism"~"^(zoo|theme_park|museum|gallery|viewpoint|attraction)$"]{around};
  nwr["leisure"~"^(escape_game|bowling_alley|water_park|ice_rink|park|nature_reserve|garden)$"]{around};
  nwr["amenity"~"^(theatre|cinema|arts_centre|cafe|restaurant)$"]{around};
);
out center tags;
""".strip()


class OverpassClient:
    def __init__(self, http: httpx.AsyncClient | None = None) -> None:
        self._http = http

    async def fetch_elements(
        self, lat: float, lng: float, radius_m: int = 10_000
    ) -> list[RawOsmElement]:
        query = build_overpass_query(lat, lng, radius_m)
        if self._http is not None:
            payload = await _post_overpass(self._http, query)
        else:
            async with httpx.AsyncClient(
                headers={"User-Agent": USER_AGENT}, timeout=60.0
            ) as client:
                payload = await _post_overpass(client, query)
        return parse_overpass_elements(payload)


async def _post_overpass(client: httpx.AsyncClient, query: str) -> dict[str, object]:
    last_error: Exception | None = None
    for url in OVERPASS_ENDPOINTS:
        try:
            response = await client.post(url, data={"data": query})
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                return data
        except httpx.HTTPError as exc:
            last_error = exc
    if last_error is not None:
        raise last_error
    return {"elements": []}


def parse_overpass_elements(payload: Mapping[str, object]) -> list[RawOsmElement]:
    raw_list = payload.get("elements")
    if not isinstance(raw_list, list):
        return []
    result: list[RawOsmElement] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue
        parsed = _parse_single_element(item)
        if parsed is not None:
            result.append(parsed)
    return result


def _parse_single_element(item: dict[str, object]) -> RawOsmElement | None:
    osm_type = item.get("type")
    osm_id = item.get("id")
    if not isinstance(osm_type, str) or not isinstance(osm_id, int):
        return None

    coords = _extract_coords(item)
    if coords is None:
        return None

    raw_tags = item.get("tags")
    tags: dict[str, str] = {}
    if isinstance(raw_tags, dict):
        for k, v in raw_tags.items():
            if isinstance(k, str) and isinstance(v, str):
                tags[k] = v

    return RawOsmElement(osm_type=osm_type, osm_id=osm_id, lat=coords[0], lng=coords[1], tags=tags)


def _extract_coords(item: dict[str, object]) -> tuple[float, float] | None:
    lat = item.get("lat")
    lon = item.get("lon")
    if isinstance(lat, int | float) and isinstance(lon, int | float):
        return float(lat), float(lon)
    center = item.get("center")
    if isinstance(center, dict):
        c_lat = center.get("lat")
        c_lon = center.get("lon")
        if isinstance(c_lat, int | float) and isinstance(c_lon, int | float):
            return float(c_lat), float(c_lon)
    return None


class WikidataClient:
    """Пакетное получение русских описаний и фотографий (P18) из Wikidata."""

    def __init__(self, http: httpx.AsyncClient | None = None) -> None:
        self._http = http

    async def fetch_enrichment(self, wikidata_ids: list[str]) -> dict[str, WikidataEnrichment]:
        unique_ids = sorted({wid for wid in wikidata_ids if wid})
        if not unique_ids:
            return {}
        if self._http is not None:
            return await _fetch_all_batches(self._http, unique_ids)
        async with httpx.AsyncClient(headers={"User-Agent": USER_AGENT}, timeout=30.0) as client:
            return await _fetch_all_batches(client, unique_ids)


async def _fetch_all_batches(
    client: httpx.AsyncClient, wikidata_ids: list[str]
) -> dict[str, WikidataEnrichment]:
    result: dict[str, WikidataEnrichment] = {}
    batch_size = 40
    for idx in range(0, len(wikidata_ids), batch_size):
        batch = wikidata_ids[idx : idx + batch_size]
        params = {
            "action": "wbgetentities",
            "ids": "|".join(batch),
            "props": "descriptions|claims",
            "languages": "ru|be|en",
            "format": "json",
        }
        try:
            response = await client.get(WIKIDATA_API_URL, params=params)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError:
            continue
        if isinstance(payload, dict):
            result.update(parse_wikidata_entities(payload))
    return result


def parse_wikidata_entities(payload: Mapping[str, object]) -> dict[str, WikidataEnrichment]:
    entities = payload.get("entities")
    if not isinstance(entities, dict):
        return {}
    result: dict[str, WikidataEnrichment] = {}
    for qid, entity in entities.items():
        if isinstance(qid, str) and isinstance(entity, dict):
            result[qid] = WikidataEnrichment(
                description=_extract_description(entity),
                image_url=_extract_p18_image(entity),
            )
    return result


def _extract_description(entity: dict[str, object]) -> str | None:
    descriptions = entity.get("descriptions")
    if not isinstance(descriptions, dict):
        return None
    for lang in ("ru", "be"):
        lang_obj = descriptions.get(lang)
        if isinstance(lang_obj, dict):
            value = lang_obj.get("value")
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _extract_p18_image(entity: dict[str, object]) -> str | None:
    claims = entity.get("claims")
    if not isinstance(claims, dict):
        return None
    p18_list = claims.get("P18")
    if not isinstance(p18_list, list) or not p18_list:
        return None
    first_claim = p18_list[0]
    if not isinstance(first_claim, dict):
        return None
    mainsnak = first_claim.get("mainsnak")
    if not isinstance(mainsnak, dict):
        return None
    datavalue = mainsnak.get("datavalue")
    if not isinstance(datavalue, dict):
        return None
    filename = datavalue.get("value")
    return commons_to_image_url(filename) if isinstance(filename, str) else None
