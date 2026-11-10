from httpx import AsyncClient

API = "/api/v1"


async def test_family_active_gets_family_places_first(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/recommendations",
        json={"city": "grodno", "tags": {"audience": ["family"], "vibe": ["active"]}},
    )

    assert response.status_code == 200
    places = response.json()["places"]
    assert places, "ожидаются результаты"
    assert all(
        "family" in {t["code"] for t in item["place"]["tags"] if t["group"] == "audience"}
        for item in places
    )
    scores = [item["score"] for item in places]
    assert scores == sorted(scores, reverse=True)
    assert scores[0] == 5  # audience (3) + vibe (2)


async def test_budget_and_indoor_filters(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/recommendations", json={"city": "grodno", "max_price": 0, "indoor": True}
    )
    for item in response.json()["places"]:
        assert item["place"]["price_level"] == 0
        assert item["place"]["is_indoor"] in (True, None)


async def test_scenarios_are_recommended(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/recommendations",
        json={"city": "grodno", "tags": {"audience": ["couple"], "vibe": ["culture"]}},
    )
    scenarios = response.json()["scenarios"]
    assert scenarios
    assert len(scenarios[0]["scenario"]["steps"]) == 2


async def test_unknown_city_returns_domain_error(client: AsyncClient) -> None:
    response = await client.post(f"{API}/recommendations", json={"city": "atlantis"})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "not_found"


async def test_invalid_budget_is_rejected(client: AsyncClient) -> None:
    response = await client.post(f"{API}/recommendations", json={"city": "grodno", "max_price": 9})
    assert response.status_code == 422


async def test_random_place(client: AsyncClient) -> None:
    response = await client.get(f"{API}/recommendations/random", params={"city": "grodno"})
    assert response.status_code == 200
    assert response.json()["name"]
