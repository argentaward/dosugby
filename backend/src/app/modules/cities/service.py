from app.core.errors import NotFoundError
from app.modules.cities.models import City
from app.modules.cities.repository import CityRepository
from app.modules.cities.schemas import CityOut


class CityService:
    def __init__(self, repository: CityRepository) -> None:
        self._repository = repository

    async def list_active(self) -> list[CityOut]:
        return [_to_out(city) for city in await self._repository.list_active()]

    async def get_active_by_slug(self, slug: str) -> CityOut:
        """Возвращает активный город или кидает NotFoundError."""
        city = await self._repository.get_active_by_slug(slug)
        if city is None:
            raise NotFoundError(f"Город '{slug}' не найден")
        return _to_out(city)


def _to_out(city: City) -> CityOut:
    return CityOut(id=city.id, slug=city.slug, name=city.name, lat=city.lat, lng=city.lng)
