# Framework imports.
from fastapi import FastAPI

from app import API_PREFIX
from app.health import route as health_router

from app.modules.entity.routes import route as entity_router
from app.modules.transaction.routes import route as transaction_router


def create_routes(app: FastAPI) -> None:
    """
    Include routes.
    """
    app.include_router(health_router, include_in_schema=False, prefix='/health')

    # Include Entity Router
    app.include_router(entity_router, tags=['Entity'], prefix=API_PREFIX)
    app.include_router(transaction_router, tags=['Transaction'], prefix=API_PREFIX)
