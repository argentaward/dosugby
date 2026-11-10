from collections.abc import Iterable

from app.modules.tags.models import Tag, TagGroup
from app.modules.tags.repository import TagRepository
from app.modules.tags.schemas import TagGroupOut, TagOptionOut, TagOut


class TagService:
    def __init__(self, repository: TagRepository) -> None:
        self._repository = repository

    async def list_groups(self) -> list[TagGroupOut]:
        groups = await self._repository.list_groups_with_tags()
        return [_group_to_out(group) for group in groups]


def tags_to_out(tags: Iterable[Tag]) -> list[TagOut]:
    """Маппинг ORM-тегов в DTO. Требует загруженного Tag.group."""
    return [
        TagOut(group=tag.group.code, code=tag.code, title=tag.title, icon=tag.icon) for tag in tags
    ]


def _group_to_out(group: TagGroup) -> TagGroupOut:
    return TagGroupOut(
        code=group.code,
        title=group.title,
        tags=[TagOptionOut(code=t.code, title=t.title, icon=t.icon) for t in group.tags],
    )
