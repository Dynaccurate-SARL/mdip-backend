from typing import Annotated, List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.drug_dto import DrugDto, DrugMappingsCount, DrugPaginatedDto
from src.application.use_cases.drug.get_all import GetDrugsUseCase
from src.application.use_cases.drug.get_by_id import GetDrugByIdUseCase
from src.application.use_cases.drug.get_paginated import GetPaginatedDrugsUseCase
from src.domain.entities.user import User
from src.domain.services.auth_service import manager
from src.infrastructure.db.base import IdInt
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.idrug_catalog_repository import IDrugCatalogRepository
from src.infrastructure.repositories.idrug_mapping_count_repository import IDrugMappingCountViewInterface
from src.infrastructure.repositories.idrug_repository import IDrugRepository
from src.utils.exc import ResourceNotFound


drug_router = APIRouter()


@drug_router.get(
    "/drugs/{drug_id}",
    status_code=status.HTTP_200_OK,
    response_model=DrugDto,
    summary="Get Drug by ID")
async def get_drug_by_id(
        session: Annotated[AsyncSession, Depends(get_session)],
        drug_id: IdInt):
    # Prepare the repository
    drug_catalog_repository = IDrugRepository(session)

    # Fetch the drug by ID
    use_case = GetDrugByIdUseCase(drug_catalog_repository)
    drug = await use_case.execute(drug_id)
    if not drug:
        return ResourceNotFound(
            detail="Drug not found"
        ).as_response(status.HTTP_404_NOT_FOUND)
    return drug


@drug_router.get(
    "/drugs",
    status_code=status.HTTP_200_OK,
    response_model=List[DrugMappingsCount],
    summary="Get all drugs filtered by name or code")
async def get_all_by_name_or_code(
        session: Annotated[AsyncSession, Depends(get_session)],
        drugnc: Annotated[str, Query(
            min_length=3, description="Filter by 'drug name' or 'drud code'")] = "",
        limit: Annotated[int, Query(ge=0)] = 0):
    # Prepare the repository
    drug_mapping_count_repository = IDrugMappingCountViewInterface(session)

    # Fetch the drug by ID
    use_case = GetDrugsUseCase(drug_mapping_count_repository)
    return await use_case.execute(drugnc, limit)


@drug_router.get(
    "/p/drugs",
    status_code=status.HTTP_200_OK,
    response_model=DrugPaginatedDto,
    summary="Get paginated drugs filtered by name or code")
async def get_drugs(
        user: Annotated[User, Depends(manager)],
        session: Annotated[AsyncSession, Depends(get_session)],
        drugnc: Annotated[str, Query(
            min_length=3, description="Filter by 'drug name' or 'drud code'")] = "",
        page: Annotated[int, Query(gt=0, example=1)] = 1,
        psize: Annotated[int, Query(gt=0, le=100, example=10)] = 10,
        catalog: Annotated[IdInt, Query(...)] = None):
    # Prepare the repository
    drug_catalog_repository = IDrugCatalogRepository(session)
    drug_repository = IDrugRepository(session)

    # Fetch paginated drugs
    try:
        use_case = GetPaginatedDrugsUseCase(
            drug_catalog_repository, drug_repository)
        return await use_case.execute(page, psize, drugnc, catalog)
    except ResourceNotFound as err:
        return err.as_response(status.HTTP_404_NOT_FOUND)
