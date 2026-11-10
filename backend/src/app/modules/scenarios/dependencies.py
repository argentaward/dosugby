from typing import Annotated

from fastapi import Depends

from app.core.db import SessionDep
from app.modules.scenarios.repository import ScenarioRepository
from app.modules.scenarios.service import ScenarioService


def get_scenario_service(session: SessionDep) -> ScenarioService:
    return ScenarioService(ScenarioRepository(session))


ScenarioServiceDep = Annotated[ScenarioService, Depends(get_scenario_service)]
