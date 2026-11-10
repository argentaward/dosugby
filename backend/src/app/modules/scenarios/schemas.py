from pydantic import BaseModel

from app.modules.tags.schemas import TagOut


class ScenarioStepOut(BaseModel):
    position: int
    place_id: int
    place_name: str
    note: str


class ScenarioCard(BaseModel):
    id: int
    title: str
    description: str
    duration_min: int | None
    tags: list[TagOut]
    steps: list[ScenarioStepOut]
