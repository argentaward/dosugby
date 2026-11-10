from app.modules.ingestion.classifier import (
    RawOsmElement,
    classify_osm_element,
    commons_to_image_url,
)


def _elem(osm_id: int = 10, **tags: str) -> RawOsmElement:
    return RawOsmElement(
        osm_type="node",
        osm_id=osm_id,
        lat=53.68,
        lng=23.83,
        tags=tags,
    )


class TestClassifyOsmElement:
    def test_classifies_museum_with_tags_and_address(self) -> None:
        raw = _elem(
            42,
            **{
                "name:ru": "Старый замок",
                "tourism": "museum",
                "addr:street": "Замковая улица",
                "addr:housenumber": "20",
                "opening_hours": "Tu-Su 10:00-18:00",
                "contact:instagram": "@grodno_castle",
                "wikidata": "Q2992522",
            },
        )
        place = classify_osm_element(raw)

        assert place is not None
        assert place.external_id == "node/42"
        assert place.name == "Старый замок"
        assert place.category_label == "Музей"
        assert place.summary == "Музей · Замковая улица, 20"
        assert place.is_indoor is True
        assert place.price_level == 1
        assert place.instagram_url == "https://www.instagram.com/grodno_castle/"
        assert place.wikidata_id == "Q2992522"
        assert "vibe.culture" in place.tag_keys
        assert "audience.family" in place.tag_keys

    def test_skips_unnamed_or_noise_places(self) -> None:
        assert classify_osm_element(_elem(1, leisure="park")) is None
        assert classify_osm_element(_elem(2, name="Столовая №3", amenity="restaurant")) is None
        assert classify_osm_element(_elem(3, name="Банкомат", amenity="atm")) is None

    def test_respects_explicit_fee_and_indoor_overrides(self) -> None:
        raw = _elem(7, name="Летний кинотеатр", amenity="cinema", fee="no", indoor="no")
        place = classify_osm_element(raw)

        assert place is not None
        assert place.price_level == 0
        assert place.is_indoor is False


class TestCommonsToImageUrl:
    def test_converts_file_prefix_and_plain_filename(self) -> None:
        url1 = commons_to_image_url("File:Grodno Castle.jpg")
        url2 = commons_to_image_url("Grodno_Castle.jpg")
        assert (
            url1
            == "https://commons.wikimedia.org/wiki/Special:FilePath/Grodno_Castle.jpg?width=800"
        )
        assert url2 == url1

    def test_converts_wiki_file_page_url(self) -> None:
        url = commons_to_image_url("https://commons.wikimedia.org/wiki/File:Kolozha.jpg")
        assert url == "https://commons.wikimedia.org/wiki/Special:FilePath/Kolozha.jpg?width=800"

    def test_ignores_category_or_empty(self) -> None:
        assert commons_to_image_url(None) is None
        assert commons_to_image_url("Category:Grodno") is None
