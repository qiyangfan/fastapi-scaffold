from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def make_client() -> TestClient:
    return TestClient(create_app(Settings(app_env="test", log_level="ERROR")))


def test_live() -> None:
    response = make_client().get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "up"}


def test_ready() -> None:
    response = make_client().get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {"status": "up"}
