"""Чистый классификатор объектов OpenStreetMap в модель досуга Dosug.

Не зависит от БД, HTTP и FastAPI (проверяется import-linter).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Final
from urllib.parse import quote


@dataclass(frozen=True, slots=True)
class RawOsmElement:
    osm_type: str
    osm_id: int
    lat: float
    lng: float
    tags: Mapping[str, str]


@dataclass(frozen=True, slots=True)
class _CategoryRule:
    key: str
    value: str
    label: str
    price_level: int
    is_indoor: bool | None
    tag_keys: frozenset[str]


@dataclass(frozen=True, slots=True)
class ClassifiedPlace:
    external_source: str
    external_id: str
    name: str
    category_label: str
    summary: str
    address: str
    lat: float
    lng: float
    price_level: int
    is_indoor: bool | None
    opening_hours: str | None
    phone: str | None
    website_url: str | None
    instagram_url: str | None
    wikidata_id: str | None
    commons_image_url: str | None
    tag_keys: frozenset[str]


def _rule(
    key: str,
    value: str,
    label: str,
    price: int,
    indoor: bool | None,
    tags: tuple[str, ...],
) -> _CategoryRule:
    return _CategoryRule(key, value, label, price, indoor, frozenset(tags))


# Порядок важен: сначала узкие категории (замки, музеи, квесты), затем общие (парки, кафе).
_RULES: Final[tuple[_CategoryRule, ...]] = (
    _rule(
        "historic",
        "castle",
        "Замок",
        1,
        None,
        ("audience.family", "audience.couple", "audience.solo", "vibe.culture"),
    ),
    _rule(
        "tourism",
        "zoo",
        "Зоопарк",
        1,
        False,
        ("audience.family", "audience.couple", "vibe.active", "vibe.calm"),
    ),
    _rule(
        "tourism",
        "theme_park",
        "Парк развлечений",
        1,
        False,
        ("audience.family", "audience.friends", "vibe.active"),
    ),
    _rule(
        "tourism",
        "museum",
        "Музей",
        1,
        True,
        ("audience.family", "audience.couple", "audience.solo", "vibe.culture"),
    ),
    _rule(
        "tourism",
        "gallery",
        "Галерея",
        1,
        True,
        ("audience.couple", "audience.solo", "vibe.culture", "vibe.calm"),
    ),
    _rule(
        "tourism",
        "viewpoint",
        "Смотровая площадка",
        0,
        False,
        ("audience.couple", "audience.solo", "audience.family", "vibe.calm", "vibe.culture"),
    ),
    _rule(
        "tourism",
        "attraction",
        "Достопримечательность",
        0,
        None,
        ("audience.family", "audience.couple", "audience.solo", "vibe.culture", "vibe.calm"),
    ),
    _rule(
        "leisure",
        "escape_game",
        "Квест-комната",
        2,
        True,
        ("audience.friends", "audience.family", "audience.couple", "vibe.active"),
    ),
    _rule(
        "leisure",
        "bowling_alley",
        "Боулинг",
        2,
        True,
        ("audience.friends", "audience.family", "audience.couple", "vibe.active"),
    ),
    _rule(
        "leisure",
        "water_park",
        "Аквапарк",
        2,
        True,
        ("audience.family", "audience.friends", "vibe.active"),
    ),
    _rule(
        "leisure",
        "ice_rink",
        "Каток",
        1,
        True,
        ("audience.family", "audience.couple", "audience.friends", "vibe.active"),
    ),
    _rule(
        "leisure",
        "park",
        "Парк",
        0,
        False,
        ("audience.family", "audience.couple", "audience.solo", "vibe.calm", "vibe.active"),
    ),
    _rule(
        "leisure",
        "nature_reserve",
        "Лесопарк",
        0,
        False,
        ("audience.family", "audience.friends", "audience.solo", "vibe.active", "vibe.calm"),
    ),
    _rule(
        "leisure",
        "garden",
        "Сад",
        0,
        False,
        ("audience.family", "audience.couple", "audience.solo", "vibe.calm"),
    ),
    _rule(
        "amenity",
        "theatre",
        "Театр",
        2,
        True,
        ("audience.couple", "audience.family", "audience.solo", "vibe.culture"),
    ),
    _rule(
        "amenity",
        "cinema",
        "Кинотеатр",
        1,
        True,
        ("audience.couple", "audience.friends", "audience.family", "vibe.culture", "vibe.calm"),
    ),
    _rule(
        "amenity",
        "arts_centre",
        "Арт-пространство",
        1,
        True,
        ("audience.couple", "audience.friends", "audience.solo", "vibe.culture"),
    ),
    _rule(
        "amenity",
        "cafe",
        "Кофейня и кафе",
        1,
        True,
        ("audience.couple", "audience.friends", "audience.solo", "vibe.food", "vibe.calm"),
    ),
    _rule(
        "amenity",
        "restaurant",
        "Ресторан",
        2,
        True,
        ("audience.couple", "audience.friends", "audience.family", "vibe.food"),
    ),
)

_SKIP_NAME_SUBSTRINGS: Final[tuple[str, ...]] = ("столовая", "буфет", "шаурма", "киоск")


def classify_osm_element(element: RawOsmElement) -> ClassifiedPlace | None:
    """Преобразует сырой объект OSM в ClassifiedPlace или возвращает None, если он не подходит."""
    tags = element.tags
    name = (tags.get("name:ru") or tags.get("name") or "").strip()
    if not name or _is_noise_name(name):
        return None

    rule = _match_rule(tags)
    if rule is None:
        return None

    address = _format_address(tags)
    summary = f"{rule.label} · {address}" if address else rule.label

    return ClassifiedPlace(
        external_source="osm",
        external_id=f"{element.osm_type}/{element.osm_id}",
        name=name[:200],
        category_label=rule.label,
        summary=summary[:300],
        address=address[:300],
        lat=element.lat,
        lng=element.lng,
        price_level=_resolve_price(tags, rule.price_level),
        is_indoor=_resolve_indoor(tags, rule.is_indoor),
        opening_hours=_clean_optional(tags.get("opening_hours"), 300),
        phone=_clean_optional(tags.get("contact:phone") or tags.get("phone"), 32),
        website_url=_clean_optional(tags.get("contact:website") or tags.get("website"), 500),
        instagram_url=_normalize_instagram(tags.get("contact:instagram") or tags.get("instagram")),
        wikidata_id=_clean_wikidata(tags.get("wikidata")),
        commons_image_url=commons_to_image_url(tags.get("image") or tags.get("wikimedia_commons")),
        tag_keys=rule.tag_keys,
    )


def commons_to_image_url(raw_value: str | None) -> str | None:
    """Преобразует имя файла Wikimedia Commons или прямую ссылку в URL изображения."""
    if not raw_value:
        return None
    cleaned = raw_value.strip()
    if cleaned.startswith(("http://", "https://")) and not cleaned.startswith(
        "https://commons.wikimedia.org/wiki/File:"
    ):
        return cleaned[:500]
    if cleaned.startswith("https://commons.wikimedia.org/wiki/File:"):
        filename = cleaned.removeprefix("https://commons.wikimedia.org/wiki/File:")
        return _build_filepath_url(filename)
    if cleaned.lower().startswith("file:"):
        return _build_filepath_url(cleaned[5:])
    if not cleaned.lower().startswith("category:") and "." in cleaned:
        return _build_filepath_url(cleaned)
    return None


def _build_filepath_url(filename: str) -> str:
    safe_name = quote(filename.strip().replace(" ", "_"))
    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{safe_name}?width=800"


def _is_noise_name(name: str) -> bool:
    lowered = name.lower()
    return any(word in lowered for word in _SKIP_NAME_SUBSTRINGS)


def _match_rule(tags: Mapping[str, str]) -> _CategoryRule | None:
    for rule in _RULES:
        if tags.get(rule.key) == rule.value:
            return rule
    return None


def _format_address(tags: Mapping[str, str]) -> str:
    street = (tags.get("addr:street:ru") or tags.get("addr:street") or "").strip()
    house = (tags.get("addr:housenumber") or "").strip()
    if street and house:
        return f"{street}, {house}"
    return street


def _resolve_price(tags: Mapping[str, str], default_price: int) -> int:
    fee = tags.get("fee", "").lower()
    if fee == "no":
        return 0
    if fee == "yes" and default_price == 0:
        return 1
    return default_price


def _resolve_indoor(tags: Mapping[str, str], default_indoor: bool | None) -> bool | None:
    indoor = tags.get("indoor", "").lower()
    if indoor == "yes":
        return True
    if indoor == "no":
        return False
    return default_indoor


def _clean_optional(value: str | None, max_len: int) -> str | None:
    if not value:
        return None
    stripped = value.strip()
    return stripped[:max_len] if stripped else None


def _clean_wikidata(value: str | None) -> str | None:
    if not value:
        return None
    first = value.split(";")[0].strip()
    return first if first.startswith("Q") and first[1:].isdigit() else None


def _normalize_instagram(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip()
    if not cleaned:
        return None
    if cleaned.startswith(("http://", "https://")):
        return cleaned[:500]
    handle = cleaned.lstrip("@").strip("/")
    return f"https://www.instagram.com/{handle}/" if handle else None
