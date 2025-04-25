from fastapi import FastAPI

from src.config.constants import C
from src.presentation.routes.health import health_router
from src.presentation.routes.authentication import auth_router
from src.presentation.routes.user import user_router
from src.presentation.routes.drug import drug_router
from src.presentation.routes.drug_catalog import drug_catalog_router
from src.presentation.routes.mapping import mapping_router


def register_api_routes(app: FastAPI):
    app.include_router(health_router, include_in_schema=False,
                       prefix=f'{C.URL_PREFIX}/health')
    app.include_router(auth_router, tags=['Authentication'],
                       prefix=C.URL_PREFIX)
    app.include_router(user_router, tags=['User'],
                       prefix=C.URL_PREFIX)
    app.include_router(drug_catalog_router, tags=['Drug Catalog'],
                       prefix=C.URL_PREFIX)
    app.include_router(drug_router, tags=['Drug'],
                       prefix=C.URL_PREFIX)
    app.include_router(mapping_router, tags=['Mapping'],
                       prefix=C.URL_PREFIX)
