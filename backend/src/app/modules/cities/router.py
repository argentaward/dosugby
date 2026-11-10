from fastapi import APIRouter

from app.modules.cities.dependencies import CityServiceDep
from app.modules.cities.schemas import CityOut

router = APIRouter(prefix="/cities", tags=["cities"])


@router.get("", summary="РЎРїРёСЃРѕРє Р°РєС‚РёРІРЅС‹С… РіРѕСЂРѕРґРѕРІ")
async def list_cities(service: CityServiceDep) -> list[CityOut]:
    return await service.list_active()
