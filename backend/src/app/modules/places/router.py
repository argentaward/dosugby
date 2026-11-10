from fastapi import APIRouter, status

from app.modules.places.dependencies import PlaceServiceDep
from app.modules.places.schemas import PlaceDetail, PlaceReportCreate, PlaceReportOut

router = APIRouter(prefix="/places", tags=["places"])


@router.get("/{place_id}", summary="Карточка места")
async def get_place(place_id: int, service: PlaceServiceDep) -> PlaceDetail:
    return await service.get_detail(place_id)


@router.post(
    "/{place_id}/reports",
    status_code=status.HTTP_201_CREATED,
    summary="Сообщить о неактуальных данных",
)
async def report_place(
    place_id: int, data: PlaceReportCreate, service: PlaceServiceDep
) -> PlaceReportOut:
    return await service.report(place_id, data)
