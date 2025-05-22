from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.stats.get_admin_stats import GetAdminStatsUseCase
from src.domain.entities.user import User
from src.domain.services.auth_service import manager
from src.application.dto.stats_dto import AdminStatsDto, StatsKind
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.idrug_catalog_repository import (
    IDrugCatalogRepository,
)
from src.infrastructure.repositories.imapping_repository import IMappingRepository


stats_router = APIRouter()


@stats_router.get(
    "/admin/stats", response_model=AdminStatsDto, summary="Get admin stats"
)
async def get_stats(
    user: Annotated[User, Depends(manager)],
    session: Annotated[AsyncSession, Depends(get_session)],
    kind: Annotated[StatsKind, Query(...)] = "all",
):
    drug_catalog_repository = IDrugCatalogRepository(session)
    mapping_repository = IMappingRepository(session)

    usecase = GetAdminStatsUseCase(drug_catalog_repository, mapping_repository)
    return await usecase.execute(kind)
