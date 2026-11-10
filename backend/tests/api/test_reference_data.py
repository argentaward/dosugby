from httpx import AsyncClient

API = "/api/v1"


async def test_health(client: AsyncClient) -> None:
    response = await client.get(f"{API}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_cities(client: AsyncClient) -> None:
    response = await client.get(f"{API}/cities")
    assert response.status_code == 200
    assert [c["slug"] for c in response.json()] == ["grodno"]


async def test_tag_groups_are_quiz_steps(client: AsyncClient) -> None:
    response = await client.get(f"{API}/tags")
    groups = {g["code"]: g for g in response.json()}
    assert list(groups) == ["audience", "vibe"]
    assert "family" in {t["code"] for t in groups["audience"]["tags"]}
