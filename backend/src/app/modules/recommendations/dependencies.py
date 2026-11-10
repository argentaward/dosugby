from typing import Annotated

from fastapi import Depends

from app.modules.cities.dependencies import CityServiceDep
from app.modules.places.dependencies import PlaceServiceDep
from app.modules.recommendations.service import RecommendationService
from app.modules.scenarios.dependencies import ScenarioServiceDep


def get_recommendation_service(
    cities: CityServiceDep, places: PlaceServiceDep, scenarios: ScenarioServiceDep
) -> RecommendationService:
    return RecommendationService(cities, places, scenarios)


RecommendationServiceDep = Annotated[RecommendationService, Depends(get_recommendation_service)]
