"""Run FastAPI application."""

from dishka import Provider
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.di_container import create_container
from app.di_container.settings import settings
from app.handler.api import create_web_app


def make_app(*di_providers: Provider) -> FastAPI:
    """Create FastAPI app with DI container.

    Args:
        *di_providers: Additional providers for testing

    Returns:
        Configured FastAPI application
    """
    app: FastAPI = create_web_app()
    container = create_container(*di_providers)
    setup_dishka(container, app)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app=make_app(),
        host=settings.server.host,
        port=settings.server.port,
        reload=False,
        loop="uvloop",
    )
