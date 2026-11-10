from typing import Annotated

from fastapi import Depends

from app.core.db import SessionDep
from app.modules.cities.repository import CityRepository
from app.modules.cities.service import CityService


def get_city_service(session: SessionDep) -> CityService:
    return CityService(CityRepository(session))


CityServiceDep = Annotated[CityService, Depends(get_city_service)]
