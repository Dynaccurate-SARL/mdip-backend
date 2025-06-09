import uuid
from typing import Annotated
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from fastapi import Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.dto.drug_catalog_dto import (
    CountryCode,
    DrugCatalogCreateDto,
    DrugCatalogCreatedDto,
    DrugCatalogDto,
    DrugCatalogPaginatedDto,
)
from src.application.use_cases.drug_catalog.get_by_id import GetDrugCatalogByIdUseCase
from src.application.use_cases.drug_catalog.get_paginated import (
    GetPaginatedDrugCatalogUseCase,
)
from src.application.use_cases.drug_catalog.import_task import CatalogImportUseCase
from src.config.settings import get_config
from src.domain.entities.user import User
from src.domain.services.auth_service import manager
from src.infrastructure.db.base import IdInt
from src.infrastructure.db.engine import get_session
from src.infrastructure.repositories.icatalog_transaction_repository import (
    ICatalogTransactionRepository,
)
from src.infrastructure.repositories.idrug_catalog_repository import (
    IDrugCatalogRepository,
)
from src.infrastructure.repositories.idrug_repository import IDrugRepository
from src.application.use_cases.drug_catalog.create import DrugCatalogCreateUseCase
from src.infrastructure.services.blob_storage.azure_storage import AzureFileService
from src.infrastructure.services.blob_storage.disk_storage import DiskFileService
from src.infrastructure.services.pandas_parser.drug.exc import InvalidFileFormat
from src.infrastructure.services.pandas_parser.drug.impl import drug_parser_factory
from src.infrastructure.services.confidential_ledger import ledger_builder
from src.utils.exc import ConflictErrorCode
from src.utils.file import read_chunk


drug_catalog_router = APIRouter()


@drug_catalog_router.get(
    "/catalogs/{catalog_id}",
    status_code=status.HTTP_200_OK,
    response_model=DrugCatalogDto,
)
async def get_catalog_by_id(
    catalog_id: IdInt,
    session: Annotated[AsyncSession, Depends(get_session)],
    user: Annotated[User, Depends(manager)],
):
    # Prepare the repository
    drug_catalog_repository = IDrugCatalogRepository(session)

    # Fetch the catalog by ID
    use_case = GetDrugCatalogByIdUseCase(drug_catalog_repository)
    drug_catalog = await use_case.execute(catalog_id)
    if not drug_catalog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Drug catalog not found"
        )
    return drug_catalog


@drug_catalog_router.get(
    "/p/catalogs",
    status_code=status.HTTP_200_OK,
    response_model=DrugCatalogPaginatedDto,
    summary="Get paginated drug catalogs",
)
async def get_catalogs(
    user: Annotated[User, Depends(manager)],
    session: Annotated[AsyncSession, Depends(get_session)],
    page: Annotated[int, Query(gt=0, example=1)] = 1,
    psize: Annotated[int, Query(gt=0, example=10)] = 10,
    name: Annotated[str, Query(...)] = "",
):
    # Prepare the repository
    drug_catalog_repository = IDrugCatalogRepository(session)

    # Fetch paginated catalogs
    use_case = GetPaginatedDrugCatalogUseCase(drug_catalog_repository)
    return await use_case.execute(page, psize, name)


async def drug_catalog_import_task(use_case: CatalogImportUseCase):
    await use_case.execute()


@drug_catalog_router.post(
    "/catalogs",
    status_code=status.HTTP_201_CREATED,
    response_model=DrugCatalogCreatedDto,
    summary="Create a new drug catalog",
)
async def create_catalog(
    background_tasks: BackgroundTasks,
    user: Annotated[User, Depends(manager)],
    session: Annotated[AsyncSession, Depends(get_session)],
    # http form data
    file: Annotated[UploadFile, File(...)],
    name: Annotated[str, Form(examples=["Pharmaceutical Catalog"])],
    country: Annotated[CountryCode, Form(examples=["US"])],
    version: Annotated[str, Form(examples=["1.0"])],
    is_central: Annotated[bool, Form(...)] = False,
    notes: Annotated[str, Form(examples=["Initial release"])] = "",
):
    try:
        file_bytes = await read_chunk(file)
        parser = drug_parser_factory(country, file_bytes)
    except InvalidFileFormat as err:
        return err.as_response(status_code=status.HTTP_400_BAD_REQUEST)

    # Prepare the dependencies for the create catalog use case
    drug_catalog_repository = IDrugCatalogRepository(session)
    try:
        # Create a new drug catalog entry in the database
        data = DrugCatalogCreateDto(
            name=name,
            country=country,
            version=version,
            notes=notes,
            is_central=is_central,
        )
        drug_catalog_use_case = DrugCatalogCreateUseCase(
            drug_catalog_repository=drug_catalog_repository
        )
        result = await drug_catalog_use_case.execute(data)
    except ConflictErrorCode as e:
        return e.as_response(status_code=status.HTTP_409_CONFLICT)

    # rename filename to ensure uniqueness
    file.filename = f"{str(uuid.uuid4())}_{file.filename}"

    # Upload file to the appropriate storage strategy
    if get_config().UPLOAD_STRATEGY == "AZURE":
        AzureFileService(
            get_config().AZURE_BLOB_CONTAINER_NAME,
            get_config().AZURE_BLOB_STORAGE_CONNECTION_STRING,
        ).upload_file(file.filename, file_bytes)
    if get_config().UPLOAD_STRATEGY == "DISK":
        DiskFileService(get_config().DOCUMENTS_STORAGE_PATH).upload_file(
            file.filename, file_bytes
        )

    # Prepare the dependencies for the import task use case
    transaction_repository = ICatalogTransactionRepository(session)
    drug_repository = IDrugRepository(session)
    ledger_service = ledger_builder(
        get_config().AZURE_LEDGER_URL, get_config().AZURE_CERTIFICATE_PATH
    )

    use_case = CatalogImportUseCase(
        drug_catalog_repository=drug_catalog_repository,
        transaction_repository=transaction_repository,
        drug_repository=drug_repository,
        ledger_service=ledger_service,
        catalog_id=int(result.id),
        parser=parser,
        session=session,
    )
    await use_case.prepare_task(file)
    # Add task to be processed in the background tasks
    background_tasks.add_task(drug_catalog_import_task, use_case=use_case)

    return result
