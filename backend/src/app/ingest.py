"""CLI-скрипт автоматического сбора мест из OpenStreetMap (Overpass API) + Wikidata.

Пример запуска:
    python -m uv run python -m app.ingest --city grodno --radius 10000
"""

import argparse
import asyncio

from app.core.db import engine, session_factory
from app.modules.ingestion.clients import OverpassClient, WikidataClient
from app.modules.ingestion.repository import IngestionRepository
from app.modules.ingestion.service import IngestionService
from app.seed import seed


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Импорт мест отдыха из OpenStreetMap + Wikidata")
    parser.add_argument("--city", default="grodno", help="slug города (по умолчанию: grodno)")
    parser.add_argument("--radius", type=int, default=10_000, help="радиус поиска в метрах")
    return parser.parse_args()


async def _run(city_slug: str, radius_m: int) -> None:
    async with session_factory() as session:
        await seed(session)
        service = IngestionService(
            repository=IngestionRepository(session),
            overpass=OverpassClient(),
            wikidata=WikidataClient(),
        )
        stats = await service.ingest_city(city_slug=city_slug, radius_m=radius_m)

    await engine.dispose()
    print(
        f"Готово ({stats.city_slug}): получено из OSM={stats.fetched_raw}, "
        f"прошло фильтр={stats.classified}, создано={stats.created}, "
        f"обновлено={stats.updated}, добавлено фото={stats.photos_added}"
    )


if __name__ == "__main__":
    args = _parse_args()
    asyncio.run(_run(args.city, args.radius))
