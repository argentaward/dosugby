import secrets
from collections import defaultdict
from collections.abc import Iterable

from app.core.errors import NotFoundError
from app.modules.cities.service import CityService
from app.modules.places.schemas import PlaceCard
from app.modules.places.service import PlaceService
from app.modules.recommendations.schemas import (
    RecommendationRequest,
    RecommendationResponse,
    ScoredPlace,
    ScoredScenario,
)
from app.modules.recommendations.scoring import Candidate, Preferences, TagsByGroup, rank
from app.modules.scenarios.schemas import ScenarioCard
from app.modules.scenarios.service import ScenarioService
from app.modules.tags.schemas import TagOut


class RecommendationService:
    def __init__(
        self, cities: CityService, places: PlaceService, scenarios: ScenarioService
    ) -> None:
        self._cities = cities
        self._places = places
        self._scenarios = scenarios

    async def recommend(self, request: RecommendationRequest) -> RecommendationResponse:
        """Подобрать места и сценарии в городе под предпочтения пользователя."""
        city = await self._cities.get_active_by_slug(request.city)
        prefs = Preferences(
            tags={group: frozenset(codes) for group, codes in request.tags.items() if codes},
            max_price=request.max_price,
            indoor=request.indoor,
        )

        places = {p.id: p for p in await self._places.list_cards_in_city(city.id)}
        scenarios = {s.id: s for s in await self._scenarios.list_cards_in_city(city.id)}

        ranked_places = rank(map(_place_candidate, places.values()), prefs, request.limit)
        ranked_scenarios = rank(map(_scenario_candidate, scenarios.values()), prefs, request.limit)

        return RecommendationResponse(
            places=[
                ScoredPlace(place=places[item.candidate.id], score=item.score)
                for item in ranked_places
            ],
            scenarios=[
                ScoredScenario(scenario=scenarios[item.candidate.id], score=item.score)
                for item in ranked_scenarios
            ],
        )

    async def random_place(self, city_slug: str) -> PlaceCard:
        """«Мне повезёт»: случайное опубликованное место в городе."""
        city = await self._cities.get_active_by_slug(city_slug)
        places = await self._places.list_cards_in_city(city.id)
        if not places:
            raise NotFoundError(f"В городе '{city_slug}' пока нет мест")
        return secrets.choice(places)


def _group_tags(tags: Iterable[TagOut]) -> TagsByGroup:
    grouped: defaultdict[str, set[str]] = defaultdict(set)
    for tag in tags:
        grouped[tag.group].add(tag.code)
    return {group: frozenset(codes) for group, codes in grouped.items()}


def _place_candidate(place: PlaceCard) -> Candidate:
    return Candidate(
        id=place.id,
        tags=_group_tags(place.tags),
        price_level=place.price_level,
        is_indoor=place.is_indoor,
        is_promoted=place.is_promoted,
        has_photo=place.cover_url is not None,
        verified_at=place.verified_at,
    )


def _scenario_candidate(scenario: ScenarioCard) -> Candidate:
    return Candidate(id=scenario.id, tags=_group_tags(scenario.tags))
