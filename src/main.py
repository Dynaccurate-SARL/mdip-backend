from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

from src.config.constants import C
from src.config.settings import get_config
from src.presentation.view import register_api_routes


@asynccontextmanager
async def __lifespan(app: FastAPI):
    yield


# Application factory
def create_app() -> FastAPI:
    """Application factory."""

    # Application core
    application = FastAPI(
        title=C.TITLE,
        version=C.PROJECT_VERSION,
        # Docs prefix
        redoc_url=C.URL_PREFIX + "/redoc",
        docs_url=C.URL_PREFIX + "/docs",
        openapi_url=C.URL_PREFIX + "/docs/openapi.json",
        lifespan=__lifespan,
    )
    config = get_config()
    application.state.config = config
    application.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=config.CORS_ORIGINS,
        allow_methods=config.CORS_METHODS,
        allow_headers=config.CORS_HEADERS,
        expose_headers=["X-Reason", "X-Request-ID"],
    )

    # Register routes
    register_api_routes(application)

    # Make app
    return application


app = create_app()
