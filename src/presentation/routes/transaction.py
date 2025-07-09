from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.use_cases.transaction.verify_transaction import (
    VerifyTransactionUseCase,
)
from src.config.settings import get_config
from src.domain.entities.user import User
from src.infrastructure.db.base import IdInt
from src.domain.services.auth_service import manager
from src.application.dto.transaction import CatalogTransactionDto, TransactionDto
from src.application.dto.transaction import MappingTransactionDto
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.icatalog_transaction_repository import (
    ICatalogTransactionRepository,
)
from src.application.use_cases.transaction.get_catalog_transaction import (
    GetCatalogTransactionsUseCase,
)
from src.infrastructure.repositories.imapping_transaction_repository import (
    IMappingTransactionRepository,
)
from src.application.use_cases.transaction.get_mapping_transaction import (
    GetMappingTransactionUseCase,
)
from src.infrastructure.repositories.itransaction_repository import (
    ITransactionRepository,
)
from src.infrastructure.services.confidential_ledger import ledger_builder


transaction_router = APIRouter()


@transaction_router.get(
    "/transactions/catalogs/{catalog_id}", response_model=List[CatalogTransactionDto]
)
async def get_catalog_transactions(
    catalog_id: IdInt,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(manager)],
):
    ct_repository = ICatalogTransactionRepository(session)
    use_case = GetCatalogTransactionsUseCase(ct_repository)
    return await use_case.execute(catalog_id)


@transaction_router.get(
    "/transactions/catalogs/{catalog_id}/mappings",
    response_model=List[List[MappingTransactionDto]],
)
async def get_catalog_mappings_transactions(
    catalog_id: IdInt,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(manager)],
):
    mt_repository = IMappingTransactionRepository(session)
    use_case = GetMappingTransactionUseCase(mt_repository)
    return await use_case.execute(catalog_id)


@transaction_router.get(
    "/transactions/{transaction_id}/verify", response_model=TransactionDto
)
async def ledger_transaction_verification(
    transaction_id: str,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(manager)],
):
    ledger_service = ledger_builder(
        get_config().AZURE_LEDGER_URL, 
        get_config().AZURE_CREDENTIAL_CERTIFICATE_PATH,
        get_config().AZURE_CERTIFICATE_PATH,
        get_config().ENVIRONMENT
    )
    ct_repository = ITransactionRepository(session)
    use_case = VerifyTransactionUseCase(ct_repository, ledger_service)
    return await use_case.execute(transaction_id)
