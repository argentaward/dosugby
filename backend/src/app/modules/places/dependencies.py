from typing import Annotated

from fastapi import Depends

from app.core.db import SessionDep
from app.modules.places.repository import PlaceRepository
from app.modules.places.service import PlaceService


def get_place_service(session: SessionDep) -> PlaceService:
    return PlaceService(PlaceRepository(session))


PlaceServiceDep = Annotated[PlaceService, Depends(get_place_service)]
