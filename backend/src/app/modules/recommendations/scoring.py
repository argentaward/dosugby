"""Алгоритм подбора.

Только чистые функции без БД и HTTP (проверяется import-linter), поэтому
логику легко тестировать и менять независимо от остального приложения.
"""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Final

TagsByGroup = Mapping[str, frozenset[str]]

# Насколько важно совпадение в каждой группе тегов. Неизвестные группы весят DEFAULT_GROUP_WEIGHT.
GROUP_WEIGHTS: Final[Mapping[str, int]] = {"audience": 3, "vibe": 2}
DEFAULT_GROUP_WEIGHT: Final = 1

# Если пользователь выбрал теги из этих групп — кандидат обязан совпасть хотя бы по одному.
# Например, семье с детьми не нужно предлагать места «только для пар».
REQUIRED_GROUPS: Final = frozenset({"audience"})

_EMPTY: Final[frozenset[str]] = frozenset()


@dataclass(frozen=True, slots=True)
class Candidate:
    id: int
    tags: TagsByGroup
    price_level: int = 0
    is_indoor: bool | None = None
    is_promoted: bool = False
    has_photo: bool = False
    verified_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class Preferences:
    tags: TagsByGroup = field(default_factory=dict)
    max_price: int | None = None
    indoor: bool | None = None


@dataclass(frozen=True, slots=True)
class Scored:
    candidate: Candidate
    score: int


def passes_filters(candidate: Candidate, prefs: Preferences) -> bool:
    """Жёсткие фильтры: бюджет, крыша над головой, обязательные группы тегов."""
    if prefs.max_price is not None and candidate.price_level > prefs.max_price:
        return False
    if (
        prefs.indoor is not None
        and candidate.is_indoor is not None
        and candidate.is_indoor != prefs.indoor
    ):
        return False
    for group in REQUIRED_GROUPS:
        wanted = prefs.tags.get(group, _EMPTY)
        if wanted and not wanted & candidate.tags.get(group, _EMPTY):
            return False
    return True


def score(candidate: Candidate, prefs: Preferences) -> int:
    """Сумма совпавших тегов, взвешенная по важности группы."""
    return sum(
        GROUP_WEIGHTS.get(group, DEFAULT_GROUP_WEIGHT)
        * len(wanted & candidate.tags.get(group, _EMPTY))
        for group, wanted in prefs.tags.items()
    )


def rank(candidates: Iterable[Candidate], prefs: Preferences, limit: int) -> list[Scored]:
    """Отфильтровать, оценить и отсортировать кандидатов (лучшие — первыми)."""
    scored = [Scored(c, score(c, prefs)) for c in candidates if passes_filters(c, prefs)]
    scored.sort(key=_sort_key)
    return scored[:limit]


def _sort_key(item: Scored) -> tuple[int, int, int, float]:
    verified = item.candidate.verified_at.timestamp() if item.candidate.verified_at else 0.0
    return (
        -item.score,
        -int(item.candidate.is_promoted),
        -int(item.candidate.has_photo),
        -verified,
    )
