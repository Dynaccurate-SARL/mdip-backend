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
        title='Sargasso - API',
        version='0.0.1',
        # Docs prefix
        redoc_url=C.API_PREFIX + '/redoc',
        docs_url=C.API_PREFIX + '/docs',
        openapi_url=C.API_PREFIX + '/docs/openapi.json',
        lifespan=__lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=get_config().CORS_ORIGINS,
        allow_methods=get_config().CORS_METHODS,
        allow_headers=get_config().CORS_HEADERS,
        expose_headers=['X-Reason', 'X-Request-ID'],
    )

    # Register routes
    register_api_routes(application)

    # Make app
    return application


app = create_app()
