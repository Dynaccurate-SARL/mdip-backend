import asyncio

from app import API_PREFIX
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

from .views import create_routes

from app.config import get_config

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Confidential Ledger API",
    version="0.1.0",
    docs_url=f'{API_PREFIX}/docs',
    redoc_url=f'{API_PREFIX}/redoc',
    openapi_url=f'{API_PREFIX}/openapi.json',
    lifespan=lifespan
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_routes(app)
