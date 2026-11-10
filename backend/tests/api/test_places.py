from httpx import AsyncClient

API = "/api/v1"


async def test_place_detail(client: AsyncClient) -> None:
    response = await client.get(f"{API}/places/1")
    assert response.status_code == 200
    body = response.json()
    assert body["city_slug"] == "grodno"
    assert body["tags"]


async def test_missing_place_is_404(client: AsyncClient) -> None:
    response = await client.get(f"{API}/places/9999")
    assert response.status_code == 404


async def test_report_place(client: AsyncClient) -> None:
    response = await client.post(
        f"{API}/places/1/reports", json={"reason": "closed", "comment": "Закрыто на ремонт"}
    )
    assert response.status_code == 201
    assert response.json()["reason"] == "closed"


async def test_report_rejects_unknown_reason(client: AsyncClient) -> None:
    response = await client.post(f"{API}/places/1/reports", json={"reason": "boring"})
    assert response.status_code == 422
