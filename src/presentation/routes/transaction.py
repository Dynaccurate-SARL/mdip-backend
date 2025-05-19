from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User
from src.infrastructure.db.base import IdInt
from src.domain.services.auth_service import manager
from src.application.dto.transaction import CatalogTransactionDto
from src.application.dto.transaction import MappingTransactionDto
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.icatalog_transaction_repository import ICatalogTransactionRepository
from src.application.use_cases.transaction.get_catalog_transaction import GetCatalogTransactionsUseCase
from src.infrastructure.repositories.imapping_transaction_repository import IMappingTransactionRepository
from src.application.use_cases.transaction.get_mapping_transaction import GetMappingTransactionUseCase


transaction_router = APIRouter()


@transaction_router.get("/transactions/catalogs/{catalog_id}",
                        response_model=List[CatalogTransactionDto])
async def get_catalog_transactions(
        catalog_id: IdInt,
        session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[User, Depends(manager)]):
    ct_repository = ICatalogTransactionRepository(session)
    use_case = GetCatalogTransactionsUseCase(ct_repository)
    return await use_case.execute(catalog_id)


@transaction_router.get("/transactions/catalogs/{catalog_id}/mappings",
                        response_model=List[List[MappingTransactionDto]])
async def get_catalog_mappings_transactions(
        catalog_id: IdInt,
        session: Annotated[AsyncSession, Depends(get_session)],
        user: Annotated[User, Depends(manager)]):
    ct_repository = IMappingTransactionRepository(session)
    use_case = GetMappingTransactionUseCase(ct_repository)
    return await use_case.execute(catalog_id)
