from pydantic import BaseModel


class TagOut(BaseModel):
    """Тег, привязанный к месту или сценарию."""

    group: str
    code: str
    title: str
    icon: str | None


class TagOptionOut(BaseModel):
    code: str
    title: str
    icon: str | None


class TagGroupOut(BaseModel):
    """Группа тегов с вариантами выбора — один шаг квиза."""

    code: str
    title: str
    tags: list[TagOptionOut]
