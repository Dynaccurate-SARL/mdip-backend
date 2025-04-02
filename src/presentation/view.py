from fastapi import FastAPI

from src.config.constants import C
from src.presentation.routes.health import health_router
from src.presentation.routes.authentication import auth_router
from src.presentation.routes.user import user_router


def register_api_routes(app: FastAPI):
    app.include_router(health_router, include_in_schema=False,
                       prefix=f'{C.API_PREFIX}/health')
    app.include_router(auth_router, tags=['Authentication'],
                       prefix=C.API_PREFIX)
    app.include_router(user_router, tags=['User'],
                       prefix=C.API_PREFIX)
