from typing import Annotated

from fastapi import APIRouter, Query

from app.modules.places.schemas import PlaceCard
from app.modules.recommendations.dependencies import RecommendationServiceDep
from app.modules.recommendations.schemas import RecommendationRequest, RecommendationResponse

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.post("", summary="Подобрать места и сценарии")
async def recommend(
    request: RecommendationRequest, service: RecommendationServiceDep
) -> RecommendationResponse:
    return await service.recommend(request)


@router.get("/random", summary="Мне повезёт: случайное место")
async def random_place(
    city: Annotated[str, Query(description="slug города")], service: RecommendationServiceDep
) -> PlaceCard:
    return await service.random_place(city)
