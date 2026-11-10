from pydantic import BaseModel, Field

from app.modules.places.schemas import PlaceCard
from app.modules.scenarios.schemas import ScenarioCard

MAX_PRICE_LEVEL = 3


class RecommendationRequest(BaseModel):
    city: str = Field(description="slug города, например 'grodno'")
    tags: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Выбранные теги по группам: {'audience': ['family'], 'vibe': ['active']}",
    )
    max_price: int | None = Field(default=None, ge=0, le=MAX_PRICE_LEVEL)
    indoor: bool | None = Field(default=None, description="true — под крышей, false — на улице")
    limit: int = Field(default=20, ge=1, le=50)


class ScoredPlace(BaseModel):
    place: PlaceCard
    score: int


class ScoredScenario(BaseModel):
    scenario: ScenarioCard
    score: int


class RecommendationResponse(BaseModel):
    places: list[ScoredPlace]
    scenarios: list[ScoredScenario]
