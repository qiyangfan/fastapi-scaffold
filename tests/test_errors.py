from fastapi.testclient import TestClient

from app.main import create_app
from app.settings import Settings


def make_client() -> TestClient:
    return TestClient(create_app(Settings(app_env="test", log_level="ERROR")))


def test_unknown_route_returns_envelope() -> None:
    response = make_client().get("/missing")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


def test_unhandled_exception_returns_500_envelope() -> None:
    app = create_app(Settings(app_env="test", log_level="ERROR"))

    @app.get("/boom")
    async def boom() -> None:
        raise RuntimeError("boom")

    response = TestClient(app, raise_server_exceptions=False).get("/boom")

    assert response.status_code == 500
    assert response.json() == {"code": "INTERNAL_ERROR", "message": "internal server error"}
