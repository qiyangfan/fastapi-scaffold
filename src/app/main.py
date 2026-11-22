from fastapi import FastAPI

from app.api.health import router as health_router
from app.errors import register_error_handlers
from app.logging import configure_logging
from app.settings import Settings


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved = settings or Settings()
    configure_logging(resolved.log_level)

    app = FastAPI(title="service", version="0.1.0")
    app.state.settings = resolved
    register_error_handlers(app)
    app.include_router(health_router)
    return app


app = create_app()
