from fastapi import APIRouter

from app.modules.tags.dependencies import TagServiceDep
from app.modules.tags.schemas import TagGroupOut

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", summary="Группы тегов для шагов квиза")
async def list_tag_groups(service: TagServiceDep) -> list[TagGroupOut]:
    return await service.list_groups()
