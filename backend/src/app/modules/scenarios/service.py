from app.modules.scenarios.models import Scenario
from app.modules.scenarios.repository import ScenarioRepository
from app.modules.scenarios.schemas import ScenarioCard, ScenarioStepOut
from app.modules.tags.service import tags_to_out


class ScenarioService:
    def __init__(self, repository: ScenarioRepository) -> None:
        self._repository = repository

    async def list_cards_in_city(self, city_id: int) -> list[ScenarioCard]:
        scenarios = await self._repository.list_published_by_city(city_id)
        return [_to_card(scenario) for scenario in scenarios]


def _to_card(scenario: Scenario) -> ScenarioCard:
    return ScenarioCard(
        id=scenario.id,
        title=scenario.title,
        description=scenario.description,
        duration_min=scenario.duration_min,
        tags=tags_to_out(scenario.tags),
        steps=[
            ScenarioStepOut(
                position=step.position,
                place_id=step.place_id,
                place_name=step.place.name,
                note=step.note,
            )
            for step in scenario.steps
        ],
    )
