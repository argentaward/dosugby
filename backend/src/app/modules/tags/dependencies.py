from typing import Annotated

from fastapi import Depends

from app.core.db import SessionDep
from app.modules.tags.repository import TagRepository
from app.modules.tags.service import TagService


def get_tag_service(session: SessionDep) -> TagService:
    return TagService(TagRepository(session))


TagServiceDep = Annotated[TagService, Depends(get_tag_service)]
