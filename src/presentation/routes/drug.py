from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.drug_dto import DrugDto, DrugPaginatedDto
from src.application.use_cases.drug.get_all import GetAllDrugsUseCase
from src.application.use_cases.drug.get_by_id import GetDrugByIdUseCase
from src.application.use_cases.drug.get_paginated import GetPaginatedDrugUseCase
from src.infrastructure.db.base import IdInt
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.idrug_catalog_repository import IDrugCatalogRepository
from src.infrastructure.repositories.idrug_repository import IDrugRepository


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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Drug not found"
        )
    return drug


@drug_router.get(
    "/drugs",
    status_code=status.HTTP_200_OK,
    response_model=List[DrugDto],
    summary="Get all drugs filtered by name or code")
async def get_all_by_name_or_code(
        session: Annotated[AsyncSession, Depends(get_session)],
        drugnc: Annotated[str, Query(
            min_length=3, description="Filter by 'drug name' or 'drud code'")]):
    # Prepare the repository
    drug_repository = IDrugRepository(session)
    drug_catalog_repository = IDrugCatalogRepository(session)

    # Fetch the drug by ID
    use_case = GetAllDrugsUseCase(drug_catalog_repository, drug_repository)
    return await use_case.execute(drugnc)


@drug_router.get(
    "/p/drugs",
    status_code=status.HTTP_200_OK,
    response_model=DrugPaginatedDto,
    summary="Get paginated drugs filtered by name or code")
async def get_drugs(
        session: Annotated[AsyncSession, Depends(get_session)],
        page: Annotated[int, Query(gt=0, example=1)] = 1,
        psize: Annotated[int, Query(gt=0, example=10)] = 10,
        drugnc: Annotated[str, Query(
            min_length=3, description="Filter by 'drug name' or 'drud code'")] = ''):
    # Prepare the repository
    drug_catalog_repository = IDrugCatalogRepository(session)
    drug_repository = IDrugRepository(session)

    # Fetch paginated drugs
    use_case = GetPaginatedDrugUseCase(
        drug_catalog_repository, drug_repository)
    return await use_case.execute(page, psize, drugnc)
