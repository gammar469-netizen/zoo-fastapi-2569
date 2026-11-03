from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_root():
    assert client.get("/").status_code == 200


def test_docs():
    assert client.get("/docs").status_code == 200


def test_visitors_from_csv():
    response = client.get("/api/zoo-visitors?limit=2")
    assert response.status_code == 200
    data = response.json()
    assert data["resource_id"] == main.RESOURCE_ID
    assert data["fiscal_year"] == 2569
    assert len(data["data"]) == 2
    assert "สวนสัตว์" in data["data"][0]


def test_invalid_limit():
    assert client.get("/api/zoo-visitors?limit=0").status_code == 422
