from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert "CyberGuide AI" in response.text


def test_health_check() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_ask_validation() -> None:
    response = client.post("/api/ask", json={"question": ""})
    assert response.status_code == 422
