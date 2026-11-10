import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.ingestion.clients import (
    OverpassClient,
    WikidataClient,
    parse_overpass_elements,
    parse_wikidata_entities,
)
from app.modules.ingestion.repository import IngestionRepository
from app.modules.ingestion.service import IngestionService
from app.modules.places.models import Place

FAKE_OVERPASS_RESPONSE: dict[str, object] = {
    "elements": [
        {
            "type": "way",
            "id": 1001,
            "center": {"lat": 53.677, "lon": 23.825},
            "tags": {
                "name": "Новый замок",
                "historic": "castle",
                "addr:street": "Замковая улица",
                "addr:housenumber": "20",
                "wikidata": "Q2662336",
            },
        },
        {
            "type": "node",
            "id": 1002,
            "lat": 53.684,
            "lon": 23.834,
            "tags": {
                "name": "Квест-рум Тайна",
                "leisure": "escape_game",
                "phone": "+375 29 111-22-33",
            },
        },
    ]
}

FAKE_WIKIDATA_RESPONSE: dict[str, object] = {
    "entities": {
        "Q2662336": {
            "descriptions": {"ru": {"value": "Королевский дворец XVIII века в Гродно"}},
            "claims": {"P18": [{"mainsnak": {"datavalue": {"value": "New Castle in Hrodna.jpg"}}}]},
        }
    }
}


def test_parse_overpass_and_wikidata_payloads() -> None:
    elements = parse_overpass_elements(FAKE_OVERPASS_RESPONSE)
    assert len(elements) == 2
    assert elements[0].osm_type == "way"
    assert elements[0].lat == 53.677

    enriched = parse_wikidata_entities(FAKE_WIKIDATA_RESPONSE)
    assert "Q2662336" in enriched
    assert enriched["Q2662336"].description == "Королевский дворец XVIII века в Гродно"
    assert enriched["Q2662336"].image_url is not None


async def test_ingestion_service_is_idempotent(
    session_maker: async_sessionmaker[AsyncSession],
) -> None:
    def _mock_handler(request: httpx.Request) -> httpx.Response:
        if "wikidata.org" in str(request.url):
            return httpx.Response(200, json=FAKE_WIKIDATA_RESPONSE)
        return httpx.Response(200, json=FAKE_OVERPASS_RESPONSE)

    transport = httpx.MockTransport(_mock_handler)
    async with httpx.AsyncClient(transport=transport) as http_client, session_maker() as session:
        service = IngestionService(
            repository=IngestionRepository(session),
            overpass=OverpassClient(http_client),
            wikidata=WikidataClient(http_client),
        )

        first = await service.ingest_city("grodno", radius_m=5000)
        assert first.created == 2
        assert first.updated == 0
        assert first.photos_added == 1

        second = await service.ingest_city("grodno", radius_m=5000)
        assert second.created == 0
        assert second.updated == 2
        assert second.photos_added == 0

        stmt = select(Place).where(Place.external_id == "way/1001")
        castle = await session.scalar(stmt)
        assert castle is not None
        assert castle.description == "Королевский дворец XVIII века в Гродно"
